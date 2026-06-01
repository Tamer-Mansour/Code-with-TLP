# Comprehensions

A comprehension is a compact expression that builds a list, set, dict, or generator from another iterable. Idiomatic Python relies on them heavily.

## List comprehensions

```python
squares = [x * x for x in range(10)]
```

equivalent to:

```python
squares = []
for x in range(10):
    squares.append(x * x)
```

Add a condition:

```python
evens = [x for x in range(20) if x % 2 == 0]
```

Multiple loops:

```python
pairs = [(x, y) for x in range(3) for y in range(3) if x != y]
```

Read left to right: outer loop first, inner loop next.

## Set comprehensions

```python
unique_lengths = {len(w) for w in words}
```

## Dict comprehensions

```python
char_counts = {c: word.count(c) for c in set(word)}
upper_map = {k: v.upper() for k, v in d.items()}
swap = {v: k for k, v in d.items()}
```

## Generator expressions

Same syntax but with parentheses — produces values lazily, no list built:

```python
gen = (x * x for x in range(10_000_000))
sum(gen)
```

A generator expression inside a function call doesn't need the extra parens:

```python
total = sum(x * x for x in range(10))
any(x > 100 for x in values)
max(len(w) for w in words)
```

These run in constant memory, perfect for streaming over large iterables.

## When NOT to use comprehensions

When you're side-effecting or the loop is complex, a regular `for` is clearer:

```python
# BAD - using comprehension for side effects
[print(x) for x in xs]

# GOOD
for x in xs:
    print(x)
```

When your comprehension is more than two lines, split it into a helper. Readability beats cleverness.

## A useful pattern: filter + transform

```python
# the canonical "select active users' emails"
emails = [u.email for u in users if u.is_active]
```

The expression order — transform on the left, filter on the right — reads naturally: "emails of users, for users in the set, where active."

## Walrus inside comprehensions (3.8+)

```python
# only keep the result of expensive_check if positive
results = [y for x in xs if (y := expensive_check(x)) > 0]
```

## Nested comprehensions for matrices

Flatten a 2D list:

```python
flat = [x for row in matrix for x in row]
```

Transpose:

```python
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
```

(Or simply `list(zip(*matrix))`.)
