# Clean Code: Naming, Functions, and Readability

Code is read far more often than it is written. A study by Robert Martin estimated that the ratio of reading to writing code is 10:1. Clean code is code that communicates its intent so clearly that a new reader can understand it without asking the author — or without the author needing to remember what they were thinking six months ago.

## Naming

Good names eliminate the need for comments that explain *what* code does, leaving comments free to explain *why* unexpected decisions were made.

### Variables

Use names that reveal intent:

```python
# Bad: the reader must mentally decode what d is
d = 86400

# Good: self-explanatory
SECONDS_PER_DAY = 86400

# Bad: what does "e" represent?
for e in get_all():
    if e.f:
        process(e)

# Good: immediately readable
for employee in get_active_employees():
    if employee.is_eligible_for_bonus:
        calculate_bonus(employee)
```

Avoid:
- Single-letter names except for loop counters (`i`, `j`, `k`) or well-established conventions (`x`, `y` for coordinates)
- Abbreviations that aren't universally known (`usr`, `cnt`, `tmp`)
- Encodings in names (`str_name`, `int_count`) — the type is visible in the code or IDE
- Noise words that add no meaning (`data`, `info`, `object`, `manager`)

### Functions

Functions should be named with a verb describing what they do:

```python
# Bad: noun, no indication of what it does
def user_data(user_id): ...
def order(x): ...

# Good: verb + context
def fetch_user_by_id(user_id): ...
def calculate_order_total(order): ...
def send_password_reset_email(user): ...
def is_coupon_expired(coupon) -> bool: ...
```

Boolean-returning functions should sound like yes/no questions: `is_active()`, `has_permission()`, `can_withdraw(amount)`.

### Classes

Class names should be nouns describing the concept they represent:
- `UserRepository` — not `UserManager` or `UserHandler` (these hide what the class actually does)
- `PaymentProcessor` — clear about what it processes and that it processes (rather than stores or retrieves)
- `EmailValidator` — not `EmailChecker` (validator is the conventional term)

## Functions: Small and Single-Purpose

The **Single Responsibility Principle (SRP)** applied to functions: a function should do one thing, do it well, and do it only.

```python
# Bad: three responsibilities hidden in one function
def process_order(order):
    # Responsibility 1: validation
    if order.items is None or len(order.items) == 0:
        raise ValueError("Order must have at least one item")
    # Responsibility 2: payment
    charge_result = stripe.charge(order.total, order.card_token)
    if not charge_result.success:
        raise PaymentError(charge_result.message)
    # Responsibility 3: fulfilment notification
    db.save(order)
    send_email(order.user.email, "Order confirmed!")

# Good: each function does one thing
def validate_order(order):
    if not order.items:
        raise ValueError("Order must have at least one item")

def charge_order(order) -> ChargeResult:
    return stripe.charge(order.total, order.card_token)

def persist_order(order, db) -> None:
    db.save(order)

def notify_customer(order, mailer) -> None:
    mailer.send(order.user.email, "Order confirmed!")

def place_order(order, db, mailer) -> None:
    validate_order(order)
    charge_result = charge_order(order)
    if not charge_result.success:
        raise PaymentError(charge_result.message)
    persist_order(order, db)
    notify_customer(order, mailer)
```

The second version is easier to test (each piece in isolation), easier to read, and easier to change (swap the payment processor without touching notification logic).

**Signs a function is doing too much:**
- It has "and" in its name: `validate_and_save_user`
- It is longer than ~20 lines
- It has many levels of nesting (arrow code)
- You need comments to separate "sections" within the function body

## Comments: When to Use Them

**Prefer self-documenting code over comments.** Comments that restate what the code does add noise and quickly become stale (the code changes; the comment doesn't):

```python
# Bad: comment restates the code
# increment i by 1
i += 1

# Bad: comment will become wrong when the logic changes
# returns True if user is active
def check(user):
    return user.status == 'active' and not user.is_deleted

# Good: comment explains WHY, not WHAT
# Retry up to 3 times to handle transient S3 network errors (AWS SLA: 99.9%)
for attempt in range(MAX_RETRIES):
    try:
        s3.upload(file)
        break
    except S3TransientError:
        if attempt == MAX_RETRIES - 1:
            raise
        time.sleep(2 ** attempt)   # exponential back-off
```

Use comments for:
- Non-obvious algorithmic choices with a reference (e.g., "// Knuth-Morris-Pratt, see TAOCP Vol. 2 p. 257")
- Legal notices / license headers
- Warnings about surprising side effects or non-obvious constraints
- TODO items **linked to a ticket**: `# TODO(#4421): remove after v3 migration complete`

## Code Smells

A **code smell** is a surface symptom that suggests a deeper design problem. Identifying smells is a prerequisite for productive refactoring:

| Smell | Description | Fix |
|---|---|---|
| Long Method | Function > ~20 lines | Extract sub-functions by responsibility |
| Large Class | Class does too many things | Split by responsibility (SRP) |
| Magic Numbers / Strings | `if status == 3:` or `"PENDING"` scattered everywhere | Named constants or enums |
| Duplicate Code | Same logic copy-pasted in multiple places | Extract and reuse |
| Long Parameter List | `def f(a, b, c, d, e, f):` | Introduce a data object (dataclass/namedtuple) |
| Deep Nesting | 4+ levels of indentation | Early returns, guard clauses, extract functions |
| Feature Envy | Method accesses another class's data heavily | Move the method to that class |
| Primitive Obsession | Using `str` for email/currency everywhere | Introduce domain types (`Email`, `Money`) |
| Dead Code | Unreachable code, unused parameters | Delete it — version control saves it |
| Speculative Generality | Hooks, abstractions for futures that never arrive | YAGNI (You Ain't Gonna Need It) |

## Refactoring

**Refactoring** is restructuring existing code without changing its external behaviour. It is not rewriting — it is disciplined, small-step improvement. Martin Fowler's book *Refactoring* catalogues over 60 named techniques.

**Common refactoring moves:**

```python
# Extract Function: pull a code block into a named function
# Before
total = 0
for item in order.items:
    if item.quantity > 10:
        total += item.price * item.quantity * 0.9   # bulk discount
    else:
        total += item.price * item.quantity

# After
def calculate_item_total(item) -> float:
    if item.quantity > 10:
        return item.price * item.quantity * 0.9   # bulk discount
    return item.price * item.quantity

total = sum(calculate_item_total(item) for item in order.items)
```

```python
# Replace Magic Number with Symbolic Constant
# Before
if user.failed_logins >= 5:
    lock_account(user)

# After
MAX_FAILED_LOGIN_ATTEMPTS = 5
if user.failed_logins >= MAX_FAILED_LOGIN_ATTEMPTS:
    lock_account(user)
```

```python
# Introduce Guard Clause (replace nested conditionals with early returns)
# Before
def get_user_discount(user):
    if user is not None:
        if user.is_active:
            if user.tier == 'premium':
                return 0.20
            else:
                return 0.10
        else:
            return 0.0
    else:
        return 0.0

# After (each condition fails fast)
def get_user_discount(user):
    if user is None:
        return 0.0
    if not user.is_active:
        return 0.0
    if user.tier == 'premium':
        return 0.20
    return 0.10
```

**The safety net for refactoring is tests.** Never refactor without tests — without them, you cannot know whether you changed behaviour. The Red-Green-Refactor cycle of TDD is specifically designed so that refactoring happens under the protection of a passing test suite.

## A Practical Pre-PR Checklist

Before submitting a PR, ask:

- [ ] Can I understand each function's purpose from its name alone?
- [ ] Is each function doing one thing?
- [ ] Are there any magic numbers or unexplained constants?
- [ ] Is there duplicate code that could be extracted into a shared function?
- [ ] Are there comments that could be replaced with better naming?
- [ ] Does any function have more than 3 parameters? Could they be grouped into a data object?
- [ ] Is there deeply nested code that could use guard clauses?
- [ ] Is there dead code (unused variables, unreachable branches)?
- [ ] Are all `TODO` comments linked to a ticket?
