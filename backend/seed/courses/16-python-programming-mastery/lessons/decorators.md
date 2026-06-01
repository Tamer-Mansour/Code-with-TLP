# Decorators

A decorator is a function that wraps another function and returns a replacement. The `@` syntax is sugar for "pass me through this wrapper."

## The mechanics

```python
def my_decorator(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} returned {result}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b
```

is identical to:

```python
def add(a, b): ...
add = my_decorator(add)
```

## Preserving metadata

The naive wrapper above replaces `add.__name__` and `add.__doc__`. Use `functools.wraps`:

```python
from functools import wraps

def my_decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

Now `add.__name__ == "add"` still.

## Common standard-library decorators

```python
@staticmethod      # no self/cls
@classmethod       # cls instead of self
@property          # makes a method behave as an attribute
@functools.lru_cache(maxsize=128)
@functools.cache                  # 3.9+, unbounded
@dataclasses.dataclass
@contextlib.contextmanager
```

## Parameterized decorators

A decorator that takes arguments is a function that **returns a decorator**:

```python
def retry(times):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if i == times - 1:
                        raise
        return wrapper
    return decorator

@retry(times=3)
def flaky():
    ...
```

Three nested functions: outermost takes the decorator args, middle takes the function, innermost is the wrapper.

## Real-world examples

### Timing

```python
import time
from functools import wraps

def timed(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper
```

### Auth gate (Flask-ish)

```python
def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user.is_admin:
            raise PermissionError
        return fn(*args, **kwargs)
    return wrapper
```

### Caching expensive computation

```python
from functools import lru_cache

@lru_cache(maxsize=10_000)
def reverse_dns(ip):
    ...
```

## Class decorators

You can decorate classes too — `@dataclass` is the famous example. The decorator receives the class and returns a (possibly modified) class.

```python
def add_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({fields})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Foo:
    def __init__(self):
        self.x = 1
```

## Decorator order

Applied bottom-up:

```python
@cache
@timed
def fetch(url):
    ...
```

`fetch = cache(timed(fetch))` — timing happens inside the cache.

## When NOT to write one

If the wrapping happens once at a single call site, just call the wrapping function directly. Decorators shine when the same wrapping applies to many functions.
