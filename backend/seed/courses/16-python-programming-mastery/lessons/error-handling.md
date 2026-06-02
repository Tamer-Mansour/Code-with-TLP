# Error Handling and Exceptions

Errors happen. Python uses *exceptions* — objects that represent something going wrong — and a `try/except` block to catch them before they crash the program.

## The try/except block

```python
try:
    result = 10 / int(input("Divisor: "))
except ZeroDivisionError:
    print("Cannot divide by zero.")
except ValueError as e:
    print(f"Bad input: {e}")
else:
    print(f"Result: {result}")   # runs if no exception was raised
finally:
    print("Done.")               # always runs
```

- `except` catches a specific exception type.
- `as e` binds the exception object so you can inspect it.
- `else` runs only when the `try` block completes without error.
- `finally` runs regardless — good for cleanup (though context managers usually do it better).

## The exception hierarchy

All built-in exceptions inherit from `BaseException`. Most you'll handle are `Exception` subclasses:

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ValueError
    ├── TypeError
    ├── RuntimeError
    ├── OSError  (IOError, FileNotFoundError, PermissionError, ...)
    ├── LookupError (KeyError, IndexError)
    └── ArithmeticError (ZeroDivisionError, OverflowError)
```

Catching `Exception` catches almost everything. Catching `BaseException` also catches `KeyboardInterrupt` and `SystemExit` — almost never what you want.

## Raising exceptions

```python
def parse_age(s):
    age = int(s)          # raises ValueError if s is not an integer
    if age < 0:
        raise ValueError(f"Age cannot be negative, got {age}")
    return age
```

Use `raise` with an existing exception type and a helpful message. Don't raise bare `Exception` — prefer a specific type or a custom one.

## Custom exceptions

```python
class InsufficientFundsError(ValueError):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(
            f"Cannot withdraw {amount}; balance is {balance}."
        )

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount
```

Inherit from the most specific relevant base class. This lets callers catch either `InsufficientFundsError` or the broader `ValueError` depending on how much detail they want.

## Exception chaining

When catching one error and raising another, preserve the original context:

```python
try:
    data = load_config("settings.toml")
except FileNotFoundError as e:
    raise RuntimeError("Config file is missing.") from e
```

The `from e` attaches the original exception as `__cause__`, giving you the full chain in the traceback.

## Common patterns

| Pattern | Code |
|---------|------|
| Ignore specific error | `except SomeError: pass` |
| Re-raise after logging | `except SomeError: log(); raise` |
| Return a default | `except KeyError: return default_value` |
| Convert to domain error | `raise DomainError(...) from original` |

## What NOT to do

```python
# BAD: swallows all errors, including bugs
try:
    do_something()
except Exception:
    pass

# BAD: too broad — you have no idea what went wrong
try:
    ...
except:    # catches KeyboardInterrupt too!
    pass
```

Catch only the exceptions you know how to handle. Let everything else propagate so you see real bugs.

## Worked example: safe file reader

```python
def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"No permission to read {path}") from e
```

Returns `None` when the file is simply absent, re-raises as a clearer error when access is denied, and lets other `OSError` subtypes propagate normally.
