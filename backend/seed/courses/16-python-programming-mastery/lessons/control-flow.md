# Control Flow and Loops

## if / elif / else

```python
if status == "paid":
    process()
elif status == "pending":
    enqueue()
else:
    reject()
```

No parentheses on the condition. Pythonic combinations chain comparisons:

```python
if 0 <= age <= 120:
    ...
```

## Conditional expression (ternary)

```python
label = "adult" if age >= 18 else "minor"
```

## Match (Python 3.10+)

Structural pattern matching:

```python
match request:
    case {"type": "login", "user": user}:
        login(user)
    case {"type": "logout", "user": user}:
        logout(user)
    case {"type": t}:
        unknown(t)
    case _:
        raise ValueError("invalid")
```

`match` destructures dicts, lists, dataclasses, even nested patterns. Use it for clear event/state dispatch; it's not a switch (no fallthrough).

## while

```python
while not done:
    do_one()
```

Don't forget the exit condition. `while True: ... break` is common in real Python.

## for

```python
for x in [1, 2, 3]:
    print(x)
```

`for` iterates over anything that produces values — lists, tuples, strings, dicts, generators, files. There's no C-style `for(i=0; i<n; i++)`. Use `range`:

```python
for i in range(10):           # 0..9
for i in range(1, 11):        # 1..10
for i in range(0, 10, 2):     # 0,2,4,6,8
```

### Enumerate, zip, reversed

```python
for i, name in enumerate(names):
    print(i, name)

for name, score in zip(names, scores):
    ...

for x in reversed(seq):
    ...
```

### Looping over a dict

```python
for k, v in d.items():
    ...
for k in d:                    # keys (same as d.keys())
for v in d.values():
    ...
```

## break, continue, else

```python
for x in seq:
    if predicate(x):
        found = x
        break
else:
    # runs if the for loop did NOT break
    found = None
```

The `for/else` and `while/else` clauses run when the loop completes *without* a `break`. Niche but useful for search patterns.

## Exceptions as control flow (sometimes)

```python
try:
    value = parse(s)
except ValueError as e:
    log(e)
    value = default
else:
    # ran successfully
    use(value)
finally:
    cleanup()
```

Common pattern for I/O, parsing, and "Easier to Ask Forgiveness than Permission" (EAFP):

```python
try:
    return d["key"]
except KeyError:
    return None
```

vs. LBYL (Look Before You Leap):

```python
if "key" in d:
    return d["key"]
return None
```

In Python the EAFP form is often faster and more readable for exception-rare paths. For the dict case, `d.get("key")` is best.

## pass

```python
class TODO:
    pass

def not_yet():
    pass
```

The "do nothing" statement. Required where Python's grammar demands a block but you have nothing to put there yet.
