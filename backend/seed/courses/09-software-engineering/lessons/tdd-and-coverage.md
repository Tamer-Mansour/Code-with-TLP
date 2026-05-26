# TDD, Coverage, and Test Strategy

Writing tests is not just about verifying correctness — it is a design activity that shapes how code is structured. Test-Driven Development (TDD) forces you to think about the API of your code before you write it, leading to cleaner interfaces, better separation of concerns, and a comprehensive test suite as a side effect.

## TDD: Red → Green → Refactor

The TDD cycle is three steps, repeated:

1. **Red:** Write a failing test for the next small piece of behaviour (it fails because the code doesn't exist yet)
2. **Green:** Write the *minimum* code to make the test pass (resist the urge to over-engineer)
3. **Refactor:** Clean up the code while keeping tests green

The key discipline is **"minimum code to pass."** In the Green phase, you are not writing production-quality code — you are proving the test works. In the Refactor phase (protected by a passing test), you improve the design.

## TDD Worked Example: Password Strength Checker

Let's build a function that returns the strength of a password: `"weak"`, `"medium"`, or `"strong"`.

### Cycle 1: Handle the empty string

**Red:**
```python
# tests/test_password.py
from auth.password import check_strength

def test_empty_password_is_weak():
    assert check_strength("") == "weak"
```
Run pytest → `ModuleNotFoundError` (that's a form of Red — the code doesn't exist).

**Green:**
```python
# auth/password.py
def check_strength(password: str) -> str:
    return "weak"
```
Test passes.

### Cycle 2: Long password is medium

**Red:**
```python
def test_eight_char_password_is_medium():
    assert check_strength("abcdefgh") == "medium"
```
Fails (returns "weak").

**Green:**
```python
def check_strength(password: str) -> str:
    if len(password) >= 8:
        return "medium"
    return "weak"
```
Both tests pass.

### Cycle 3: Mixed-character password is strong

**Red:**
```python
def test_password_with_upper_digit_symbol_is_strong():
    assert check_strength("Hello1!x") == "strong"
```
Fails (returns "medium").

**Green:**
```python
import re

def check_strength(password: str) -> str:
    if len(password) < 8:
        return "weak"
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_symbol = bool(re.search(r'[^A-Za-z0-9]', password))
    if has_upper and has_digit and has_symbol:
        return "strong"
    return "medium"
```

### Cycle 4: Refactor

The `has_*` variables are readable but the boolean expression is dense. Refactor while tests stay green:

```python
def _has_uppercase(password: str) -> bool:
    return any(c.isupper() for c in password)

def _has_digit(password: str) -> bool:
    return any(c.isdigit() for c in password)

def _has_symbol(password: str) -> bool:
    return any(not c.isalnum() for c in password)

def check_strength(password: str) -> str:
    if len(password) < 8:
        return "weak"
    if _has_uppercase(password) and _has_digit(password) and _has_symbol(password):
        return "strong"
    return "medium"
```

All three tests still pass. The refactored version is more readable and each helper is independently testable.

## Benefits and Trade-offs of TDD

**Benefits:**
- Forces interface design before implementation — you write code that is easy to call, not just easy to write
- Zero untested features: every feature has a test by construction
- Regression safety: changes that break existing behaviour fail immediately
- Documentation: tests describe the expected behaviour in concrete terms

**Where TDD is harder:**
- UI and presentation code (tests for what the screen shows are brittle)
- Infrastructure code (setting up a real database, configuring a server)
- Exploratory prototypes (you don't know the right interface yet)
- Integration with poorly-designed external APIs (mocking them requires understanding them first)

The pragmatic approach: use TDD for business logic and calculations; use tests-after for infrastructure code; use contract tests for external API integrations.

## Types of Test Doubles

| Type | What it does | When to use |
|---|---|---|
| **Stub** | Returns pre-configured data; doesn't record calls | Replace a data source you don't control |
| **Mock** | Records calls; verifies interactions with `assert_called` | Verify that a side effect (email, notification) was triggered |
| **Fake** | Lightweight working implementation | In-memory database or message queue for tests |
| **Spy** | Real implementation + call recording | Partial verification — want real behaviour but need to check it was called |
| **Dummy** | Placeholder that is never actually used | Fill a required parameter that isn't exercised in this test |

**Prefer fakes over complex mock chains.** An in-memory repository (`InMemoryUserRepository`) is easier to understand, maintain, and reason about than a mock with five `.return_value` and `.side_effect` chained calls.

## Designing Testable Code

Code that is hard to test is usually code with hidden dependencies:

```python
# Hard to test: creates its own dependencies
class OrderService:
    def place_order(self, order):
        db = Database("postgresql://prod-db/orders")   # hardcoded!
        mailer = SendGridMailer(api_key=os.environ["SENDGRID_KEY"])  # hardcoded!
        db.save(order)
        mailer.send(order.user.email, "confirmed")

# Easy to test: dependencies are injected
class OrderService:
    def __init__(self, db: OrderRepository, mailer: Mailer):
        self.db = db
        self.mailer = mailer

    def place_order(self, order):
        self.db.save(order)
        self.mailer.send(order.user.email, "confirmed")

# In tests:
service = OrderService(db=InMemoryOrderRepo(), mailer=NullMailer())
service.place_order(order)
```

**Dependency injection** is the single most important practice for testable code. When every dependency is passed in, every dependency can be replaced with a test double.

## Test Coverage

**Code coverage** measures what fraction of code lines (or branches) are executed by the test suite:

```bash
# Python with pytest-cov
pip install pytest-cov
pytest --cov=myapp --cov-report=html --cov-report=term-missing tests/

# Output:
# Name                   Stmts   Miss  Cover   Missing
# -------------------------------------------------------
# myapp/auth/login.py       42      3    93%   67-68, 89
# myapp/orders/service.py   87      0   100%
# myapp/payments/stripe.py  31     12    61%   44-56
```

The HTML report (`htmlcov/index.html`) colour-codes every line: green = covered, red = not covered.

**Coverage is a diagnostic, not a goal:**
- 100% line coverage does not mean bug-free — you can cover every line with assertions that test nothing meaningful
- Chasing 100% often leads to testing trivial getters/setters that will never fail
- Below 60% is a signal that large areas of logic are untested — worth investigating
- 80% is a common threshold that balances thoroughness with pragmatism

**Branch coverage** is more meaningful than line coverage:

```python
def apply_discount(price, is_member):
    if is_member:               # branch: True / False
        return price * 0.9
    return price
```

A test with `is_member=True` covers both lines but only one branch. Branch coverage requires tests for both `True` and `False`.

## What to Test: A Practical Guide

| Code type | Recommended test type |
|---|---|
| Business logic / calculations | Thorough unit tests — every edge case |
| Database queries | Integration tests with a test database |
| API endpoints | Integration tests (HTTP request → response + DB state) |
| UI flows | E2E for critical paths only (login, checkout, core workflow) |
| Third-party SDK wrappers | Integration tests against sandbox/test APIs |
| Configuration parsing | Unit tests for config validation logic |
| Trivial getters / setters | Often not worth the maintenance cost |
| External API responses | Contract tests (Pact) to detect breaking changes |

## Continuous Testing in CI/CD

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/unit/ --cov=app --cov-fail-under=80

  integration-tests:
    needs: unit-tests
    services:
      postgres:
        image: postgres:15
        env: {POSTGRES_DB: test_db, POSTGRES_PASSWORD: test}
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/integration/ -v
```

Run unit tests on every push (fast, < 1 minute). Run integration tests on every PR (1–5 minutes). Run E2E and performance tests nightly or pre-release (slow).

**Flaky tests** (tests that sometimes pass and sometimes fail without code changes) must be fixed immediately. A flaky test is worse than no test: it creates alert fatigue, causes developers to re-run CI hoping for green, and trains engineers to ignore failures.
