# Refactoring and Code Smells

**Refactoring** is the practice of restructuring existing code — changing its internal structure — without changing its external behaviour. The term was popularised by Martin Fowler's 1999 book *Refactoring: Improving the Design of Existing Code*, which catalogued a systematic vocabulary of common problems and their fixes.

**Free resource:** MIT 6.102 Software Construction readings — [ocw.mit.edu/courses/6-005-software-construction-spring-2016/](https://ocw.mit.edu/courses/6-005-software-construction-spring-2016/) — includes a rigorous unit on refactoring, representation invariants, and abstract data types.

The key insight: refactoring is *not* rewriting. You make many small, safe transformations — each individually verifiable by your test suite — that together improve the structure. A comprehensive test suite is the safety net that makes refactoring possible without introducing regressions.

## Why Code Deteriorates

Code quality decays naturally over time through a process Cunningham called **technical debt**: shortcuts taken under schedule pressure, changing requirements applied to a design that didn't anticipate them, and features added by developers who didn't fully understand the existing structure. Left unaddressed, debt accumulates interest — each future change becomes harder and riskier.

## Code Smells

A **code smell** is a surface-level indicator of a deeper structural problem. Smells don't always mean the code is wrong — they are hints that something might be worth examining. The most common ones:

### Long Method

A function exceeding 20–30 lines is usually doing more than one thing. Long methods are hard to name, hard to test, and hard to understand.

**Fix:** Extract Method — identify a coherent block of statements and move it into a well-named helper function.

```python
# Before: long method
def process_order(order):
    # 40 lines: validate, apply discount, calculate tax, send email, update DB
    ...

# After: extracted into named sub-operations
def process_order(order):
    _validate_order(order)
    discounted = _apply_discount(order)
    total = _calculate_tax(discounted)
    _persist_order(total)
    _send_confirmation_email(order)
```

### Large Class (God Object)

A class that knows too much or does too much. It accumulates responsibilities over time and becomes the centre of the system — a change anywhere requires touching it.

**Fix:** Extract Class — identify a cohesive cluster of fields and methods and move them into a new, focused class.

### Duplicate Code (DRY Violation)

The same or nearly identical logic appears in two or more places. When a bug is found or a requirement changes, every copy must be updated — and one copy will inevitably be missed.

**Fix:** Extract the shared logic into a single function or class. The **DRY (Don't Repeat Yourself)** principle: every piece of knowledge must have a single, authoritative representation.

### Feature Envy

A method that spends more time accessing data of another class than its own. It belongs in the other class.

```python
# Feature Envy: BillingService knows too much about Order's internals
class BillingService:
    def calculate_total(self, order):
        subtotal = sum(item.price * item.qty for item in order.line_items)
        tax = subtotal * order.tax_rate
        return subtotal + tax - order.discount_amount

# Better: this logic belongs on Order
class Order:
    def total(self):
        subtotal = sum(item.price * item.qty for item in self.line_items)
        return subtotal + subtotal * self.tax_rate - self.discount_amount
```

### Data Clumps

The same group of data items (e.g., `street`, `city`, `country`, `postcode`) appears together repeatedly in parameter lists and class fields. They are screaming to become their own class.

**Fix:** Extract the group into a data class (`Address`, `DateRange`, `Coordinates`).

### Long Parameter List

A function with 5+ parameters is hard to call correctly and signals that the parameters belong together in a single object.

```python
# Hard to use correctly
def create_user(first_name, last_name, email, password, dob, role, is_active):
    ...

# Better: introduce a parameter object
@dataclass
class UserRegistration:
    first_name: str
    last_name: str
    email: str
    password: str
    dob: date
    role: str
    is_active: bool = True

def create_user(reg: UserRegistration):
    ...
```

### Primitive Obsession

Using primitive types (`str`, `int`) to represent domain concepts that deserve their own type. An `email: str` field has no validation; an `Email` value object enforces the invariant everywhere.

## The Refactoring Workflow

Safe refactoring follows a disciplined cycle:

1. **Make sure tests pass** — never refactor broken code
2. **Identify the smell** — name the problem
3. **Apply one small transformation** — rename, extract, move
4. **Run tests** — confirm behaviour is preserved
5. **Commit** — each small transformation is a commit; this makes it easy to revert
6. **Repeat**

Attempting a large refactoring in one step without tests is rewriting, not refactoring — and it usually breaks things.

## DRY and KISS

**DRY (Don't Repeat Yourself):** Every piece of knowledge should have one, unambiguous, authoritative representation. DRY applies to logic, data, configuration, and documentation — not just code. The opposite of DRY is WET (Write Everything Twice / We Enjoy Typing).

**KISS (Keep It Simple, Stupid):** Prefer the simplest solution that works. Simple code is easier to read, test, debug, and modify. Complexity is a cost — it must be justified by clear benefit. YAGNI (You Ain't Gonna Need It) is the planning corollary: don't add features or abstraction layers for anticipated future needs that may never materialise.

These principles don't conflict with good design — they reinforce it. A SOLID design with no duplication and no unnecessary complexity is both DRY and KISS.
