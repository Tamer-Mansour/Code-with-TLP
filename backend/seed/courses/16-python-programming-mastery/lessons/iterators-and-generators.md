# Iterators and Generators

## Iteration protocol

A Python object is **iterable** if it returns an **iterator** from `__iter__`. An iterator is an object whose `__next__` produces values and raises `StopIteration` when exhausted.

```python
for x in [1, 2, 3]:
    print(x)
```

is sugar for:

```python
it = iter([1, 2, 3])
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    print(x)
```

You rarely call `iter`/`next` directly, but knowing the protocol lets you write custom iterables.

## Generators — easy iterators

The cleanest way to make an iterator: a function with `yield`.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for x in countdown(5):
    print(x)      # 5 4 3 2 1
```

Each `yield` pauses the function and returns a value. Next call resumes from the same line with all locals intact.

## Why generators

**Lazy** — they produce values on demand. Memory stays constant even for million-element sequences:

```python
def lines_of(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")

for line in lines_of("huge.log"):
    if "ERROR" in line:
        print(line)
```

You never hold the whole file in memory.

## Generator expressions

Same as list comprehensions but with parentheses:

```python
total = sum(x * x for x in range(10_000_000))
```

Doesn't build a 10M-element list.

## Generators are pipelines

You can chain them. Each stage processes lazily:

```python
lines = lines_of("data.csv")
records = (line.split(",") for line in lines)
valid = (r for r in records if len(r) == 5)
totals = (float(r[4]) for r in valid)
print(sum(totals))
```

Each value travels through the whole pipeline once, on demand.

## itertools — the standard library jewel

```python
from itertools import islice, chain, groupby, accumulate, count

list(islice(count(1), 5))                  # [1, 2, 3, 4, 5]
list(chain([1, 2], [3, 4]))                # [1, 2, 3, 4]
list(accumulate([1, 2, 3, 4]))             # [1, 3, 6, 10]   (running sum)

for key, group in groupby(sorted(items, key=k_fn), key=k_fn):
    ...
```

`itertools` is full of these — get familiar.

## Sending values to a generator

A generator's `yield` is actually an *expression*:

```python
def echo():
    while True:
        msg = yield
        print("got:", msg)

g = echo()
next(g)            # prime
g.send("hi")       # prints "got: hi"
```

This is the basis of Python's coroutines, before `async/await` was added.

## When NOT to use a generator

- Need random access (`xs[3]`) — generators are sequential only.
- Need to iterate multiple times — generators are exhausted after one pass.

In both cases, materialize: `list(gen)`.
