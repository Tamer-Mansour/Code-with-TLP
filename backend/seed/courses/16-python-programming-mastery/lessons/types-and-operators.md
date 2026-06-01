# Types and Operators

Python is **dynamically typed** — variables have a type at runtime, not in your source. But every value has a definite type, and operators behave predictably on each.

## The built-in types

```python
True, False          # bool
42, -1, 0            # int (unbounded precision!)
3.14                 # float (64-bit)
2 + 3j               # complex
"hello"              # str
b"bytes"             # bytes
[1, 2, 3]            # list
(1, 2, 3)            # tuple (immutable)
{1, 2, 3}            # set
{"a": 1}             # dict
None                 # NoneType
```

Check with `type(x)` or `isinstance(x, int)`. Prefer `isinstance` because it respects subclasses.

## Arithmetic

```python
3 + 5      # 8
3 - 5      # -2
3 * 5      # 15
10 / 3     # 3.333...   (always float)
10 // 3    # 3          (floor division)
10 % 3     # 1
2 ** 10    # 1024
```

`/` returns float, `//` integer. Surprising the first time. Mind the negative case: `-7 // 2 == -4`, not `-3`.

## Strings

```python
s = "hello"
s.upper()           # "HELLO"
s[0]                # "h"
s[1:4]              # "ell"     (slicing)
s[::-1]             # "olleh"   (reverse)
len(s)              # 5
"l" in s            # True
s.replace("l", "L") # "heLLo"
",".join(["a","b"]) # "a,b"
"a,b".split(",")    # ["a","b"]
```

Strings are **immutable** — every method returns a new string.

### f-strings

```python
name = "Alice"
age = 30
print(f"{name} is {age}")           # Alice is 30
print(f"{age:04d}")                 # 0030
print(f"{3.14159:.2f}")             # 3.14
print(f"{name=}, {age=}")           # name='Alice', age=30   (debug form)
```

The modern way. Use them everywhere over `%` and `.format()`.

## Truthiness

`bool(x)` is `False` for: `None`, `False`, `0`, `0.0`, `""`, `b""`, `[]`, `()`, `{}`, `set()`. Everything else is truthy.

```python
if user_list:        # non-empty?
    process(user_list)
```

Pythonic. Don't write `if len(user_list) > 0:`.

## Comparisons

```python
a == b               # equal values
a is b               # same object identity
a != b
1 < x < 10           # chained comparison
```

Use `is` only for `None`: `if x is None:`.

## Logical operators

```python
True and False       # False
True or False        # True
not True             # False
x or "default"       # short-circuit; returns x if truthy else "default"
```

`and`/`or` return the operand value, not a bool — that's why `x or default` works as a fallback idiom.

## Casting

```python
int("42")           # 42
str(3.14)           # "3.14"
list("abc")         # ["a","b","c"]
bool(0), bool(1)    # False, True
```
