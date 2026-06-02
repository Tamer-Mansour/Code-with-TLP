# Context Managers

A context manager is an object that sets something up when you enter a `with` block and tears it down when you leave — even if an exception is raised. This pattern eliminates resource leaks and keeps cleanup code close to the acquisition code.

## The with statement

```python
with open("data.txt", encoding="utf-8") as f:
    contents = f.read()
# f is closed here, no matter what
```

Without a context manager you would need:

```python
f = open("data.txt")
try:
    contents = f.read()
finally:
    f.close()
```

Both are equivalent, but `with` is shorter and harder to get wrong.

## How it works: the protocol

Any object with `__enter__` and `__exit__` methods is a context manager.

```python
class Timer:
    import time

    def __enter__(self):
        self._start = __import__("time").perf_counter()
        return self                       # bound to the 'as' target

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = __import__("time").perf_counter() - self._start
        print(f"Elapsed: {elapsed:.3f}s")
        return False                      # False = don't suppress exceptions
```

Usage:

```python
with Timer() as t:
    expensive_computation()
# prints: Elapsed: 0.412s
```

`__exit__` receives the exception info if one was raised. Return `True` to suppress the exception, `False` (or `None`) to let it propagate.

## contextlib.contextmanager

Writing `__enter__`/`__exit__` by hand is verbose for simple cases. Use the generator-based decorator instead:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"Acquiring {name}")
    resource = acquire(name)         # setup
    try:
        yield resource               # code inside 'with' runs here
    finally:
        release(resource)            # teardown, even on exception
        print(f"Released {name}")
```

```python
with managed_resource("db_connection") as conn:
    conn.execute("SELECT 1")
```

The generator must `yield` exactly once. Everything before `yield` is `__enter__`; everything after (in `finally`) is `__exit__`.

## contextlib.suppress

Cleanly ignore specific exceptions:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("tmp.lock")   # no error if the file didn't exist
```

Equivalent to `try/except FileNotFoundError: pass`, but expresses intent more clearly.

## Multiple context managers in one line

```python
with open("input.txt") as src, open("output.txt", "w") as dst:
    dst.write(src.read().upper())
```

Python 3.10+ also supports parenthesised form for long lists:

```python
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    ...
```

## Common built-in context managers

| Context manager | What it manages |
|----------------|-----------------|
| `open(...)` | File handles |
| `threading.Lock()` | Thread locks |
| `decimal.localcontext()` | Decimal precision settings |
| `unittest.mock.patch(...)` | Monkey-patching in tests |
| `tempfile.TemporaryDirectory()` | Temp dirs cleaned on exit |
| `contextlib.redirect_stdout(f)` | Redirects stdout |

## When to write your own

Write a context manager whenever you have a setup/teardown pair that should always be executed together:

- Database transactions (commit on success, rollback on exception)
- Changing global state temporarily (locale, working directory, logging level)
- Acquiring and releasing locks
- Measuring performance of a code block

Context managers make the contract explicit: "this resource will be released no matter what."
