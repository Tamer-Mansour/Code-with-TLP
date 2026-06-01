# Dicts and Sets

## Dicts — key/value maps

```python
d = {"name": "Alice", "age": 30}
d["email"] = "alice@x.com"
d.get("missing", "default")
d.pop("age")              # removes and returns
"name" in d
list(d.keys()), list(d.values()), list(d.items())
del d["email"]
```

### Insertion order is preserved

Since Python 3.7+, dicts iterate in insertion order. Safe to rely on it.

### Update, merge

```python
d.update({"city": "Berlin"})
e = d | {"country": "DE"}       # 3.9+ union, new dict
d |= {"country": "DE"}          # in-place union
```

### setdefault

```python
groups = {}
for word in words:
    groups.setdefault(word[0], []).append(word)
```

Inserts `[]` only if the key was missing — atomic find-or-create.

### defaultdict

```python
from collections import defaultdict
groups = defaultdict(list)
for w in words:
    groups[w[0]].append(w)
```

Even cleaner. Available factories: `list`, `set`, `int` (good for counters), `dict`, or any callable.

### Counter

```python
from collections import Counter
c = Counter("mississippi")
c.most_common(3)               # [('i', 4), ('s', 4), ('p', 2)]
```

### Dict comprehensions

```python
{k: v.upper() for k, v in d.items()}
{x: x*x for x in range(5)}
```

## Sets — unique unordered collections

```python
s = {1, 2, 3}
s.add(4)
s.discard(2)               # no error if missing (vs s.remove which raises)
3 in s

a | b      # union
a & b      # intersection
a - b      # difference
a ^ b      # symmetric difference
a <= b     # subset
```

Empty set is `set()` — `{}` is an empty *dict*.

### Frozenset

Hashable and immutable — usable as a dict key:

```python
fs = frozenset([1, 2, 3])
```

### Set comprehensions

```python
{x % 3 for x in range(10)}    # {0, 1, 2}
```

## Performance characteristics

| Op            | dict / set | list  |
|---------------|------------|-------|
| `x in c`      | O(1)       | O(n)  |
| insert        | O(1) avg   | O(n) insert at front, O(1) append |
| iterate       | O(n)       | O(n)  |
| ordered       | yes (dict) / no (set) | yes |

Use a `set` for "have I seen this?" and a `dict` for "what's the value for this key?" — both are dramatically faster than scanning a list.

## A worked pattern

Counting things:

```python
from collections import Counter
top_words = Counter(words).most_common(10)
```

Grouping things:

```python
from collections import defaultdict
by_country = defaultdict(list)
for u in users:
    by_country[u.country].append(u)
```

These two patterns cover a huge fraction of real Python data wrangling.
