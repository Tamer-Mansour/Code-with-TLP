# Testing Fundamentals: Unit, Integration, and End-to-End

Testing verifies that software behaves as intended and protects against regressions — changes that accidentally break existing functionality. A well-tested codebase lets engineers make changes with confidence; a poorly tested one makes every release feel like defusing a bomb.

## The Testing Pyramid

The **testing pyramid** (Mike Cohn, 2009) describes the ideal distribution of test types:

```
              /\
             /  \
            / E2E \   ← few tests, slow, high confidence in real user flows
           /──────\
          /        \
         /Integration\  ← moderate count, test component boundaries
        /────────────\
       /              \
      /   Unit Tests   \  ← many, fast, cheap, isolated
     /──────────────────\
```

The pyramid shape is a guide, not a rigid rule:
- **Unit tests** should dominate because they are fastest to run, easiest to debug, and cheapest to maintain.
- **Integration tests** cover the wiring between components — critical because that's where bugs often hide.
- **E2E tests** cover full user flows — valuable but slow and brittle; use sparingly.

A common healthy ratio: 70% unit / 20% integration / 10% E2E.

## Unit Tests

A **unit test** verifies a single function or class in isolation. All dependencies (databases, APIs, file systems, randomness, clocks) are replaced with **test doubles** (mocks, stubs, or fakes).

```python
# Python with pytest
import pytest
from auth.coupon import apply_coupon

def test_apply_coupon_reduces_total():
    assert apply_coupon(100.00, "SAVE10") == 90.00

def test_apply_coupon_expired_returns_original():
    assert apply_coupon(100.00, "EXPIRED20") == 100.00

def test_apply_coupon_invalid_code_raises():
    with pytest.raises(ValueError, match="Unknown coupon"):
        apply_coupon(100.00, "NOTACODE")
```

**Properties of good unit tests:**
- Fast: each test runs in < 10 ms
- Deterministic: same result every run
- Independent: no shared mutable state between tests
- Isolated: no real database, no real network, no file system I/O
- Named descriptively: `test_apply_coupon_expired_returns_original` reads like a specification

## Integration Tests

An **integration test** verifies that two or more real components work together correctly. Typically: your code + a real database, or your service + a real dependent service.

```python
# Testing actual database persistence with pytest + SQLAlchemy
def test_user_creation_persists_to_db(db_session):
    # Arrange
    user_data = {"email": "alice@example.com", "password_hash": "xxx"}
    
    # Act
    user = create_user(db_session, **user_data)
    db_session.flush()
    
    # Assert: fetch from database to confirm persistence
    fetched = db_session.get(User, user.id)
    assert fetched is not None
    assert fetched.email == "alice@example.com"

def test_create_duplicate_email_raises(db_session):
    create_user(db_session, email="bob@example.com", password_hash="yyy")
    db_session.flush()
    
    with pytest.raises(IntegrityError):
        create_user(db_session, email="bob@example.com", password_hash="zzz")
```

Integration tests run slower (100 ms – seconds per test) because they involve real I/O. Use a test database (Docker, SQLite for simple cases) that is reset between test runs.

**API integration tests** (also called "contract tests") test your endpoints from the outside:

```python
def test_login_returns_jwt(client, seed_user):
    response = client.post("/auth/login", json={
        "email": seed_user.email,
        "password": "correct-password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password_returns_401(client, seed_user):
    response = client.post("/auth/login", json={
        "email": seed_user.email,
        "password": "wrong-password"
    })
    assert response.status_code == 401
```

## End-to-End (E2E) Tests

E2E tests simulate a real user interacting with the deployed system — browser automation tools drive the UI.

```python
# Playwright (Python)
def test_login_flow(page):
    page.goto("https://staging.myapp.com/login")
    page.fill("[data-testid=email-input]", "user@example.com")
    page.fill("[data-testid=password-input]", "correct-horse-battery")
    page.click("[data-testid=login-button]")
    
    # Wait for navigation
    page.wait_for_url("**/dashboard")
    assert "Welcome" in page.inner_text("h1")
```

E2E tests are the most realistic but also:
- Slowest (seconds to minutes per test)
- Most brittle (break when UI changes, even if logic is correct)
- Hardest to debug ("why did this fail?" often requires video replay)

Best practice: use E2E tests only for the **critical user journeys** — sign-up, login, purchase, core workflow. Everything else is better covered by unit + integration tests.

## Mocking in Depth

A **mock** replaces a real dependency with a controllable fake. Mocking is essential for:
- Calling external APIs in tests (no network required, no side effects)
- Simulating error conditions (e.g., payment gateway timeout)
- Verifying that a function was called with specific arguments

```python
from unittest.mock import patch, MagicMock, call

def test_send_welcome_email_called_after_registration():
    with patch("auth.notifications.send_email") as mock_send:
        register_user(email="alice@example.com", password="s3cret")
        
        mock_send.assert_called_once_with(
            to="alice@example.com",
            subject="Welcome to TLP!",
            template="welcome"
        )

def test_payment_gateway_timeout_raises_user_friendly_error():
    with patch("payments.stripe.charge") as mock_charge:
        mock_charge.side_effect = stripe.Timeout("Connection timed out")
        
        with pytest.raises(PaymentUnavailableError):
            process_payment(order, card_token="tok_test")
```

**Overusing mocks is a smell.** If your test mocks 5 things to test 3 lines of logic, the logic is probably in the wrong layer. Prefer testing through real interfaces with a test double at the boundary (e.g., an in-memory database).

## Testing Best Practices

**Arrange / Act / Assert (AAA):** structure each test in three clear sections:

```python
def test_calculate_discount_for_premium_user():
    # Arrange
    user = User(tier="premium", account_age_days=365)
    cart = Cart(subtotal=200.00)
    
    # Act
    discount = calculate_discount(user, cart)
    
    # Assert
    assert discount == 30.00   # 15% for premium
```

**Test the contract, not the implementation:** test what a function returns, not how it does it. Tests that assert on internal variables or call private methods break every time you refactor, defeating the purpose.

**Descriptive names:** `test_calculate_discount_with_expired_coupon_returns_zero` is more valuable than `test_discount_3`. The name serves as the error message when the test fails.

**Never commit commented-out, skipped, or permanently `xfail`-marked tests** without a reason and a linked ticket. A test that never runs is worse than no test — it creates false confidence.

**Fast feedback loops:** run the unit test suite before every commit (pre-commit hook), the full suite on every PR (CI pipeline), and E2E tests nightly or pre-release.
