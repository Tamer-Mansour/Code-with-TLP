# The collections Module

Python's `collections` module provides specialised container types that solve common problems more expressively and efficiently than plain dicts, lists, and tuples.

## Counter

`Counter` counts hashable items and returns a dict-like object keyed by element.

```python
from collections import Counter

words = "the cat sat on the mat the cat".split()
freq = Counter(words)
print(freq)
# Counter({'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})

print(freq.most_common(2))
# [('the', 3), ('cat', 2)]

# Arithmetic on counters
a = Counter("aab")
b = Counter("abc")
print(a + b)   # Counter({'a': 3, 'b': 2, 'c': 1})
print(a - b)   # Counter({'a': 1})  (negatives are dropped)
```

## defaultdict

Avoids `KeyError` when accessing a missing key by supplying a default factory.

```python
from collections import defaultdict

graph = defaultdict(list)
graph["A"].append("B")   # no need to initialise graph["A"] first
graph["A"].append("C")

word_positions = defaultdict(set)
for i, w in enumerate("the cat sat on the mat".split()):
    word_positions[w].add(i)
```

Compare to the verbose alternative: `graph.setdefault("A", []).append("B")`.

## deque

A double-ended queue with O(1) appends and pops from **both** ends. `list.insert(0, x)` is O(n); `deque.appendleft(x)` is O(1).

```python
from collections import deque

q = deque([1, 2, 3])
q.appendleft(0)     # [0, 1, 2, 3]
q.append(4)         # [0, 1, 2, 3, 4]
q.popleft()         # returns 0 → [1, 2, 3, 4]

# Fixed-size sliding window (maxlen automatically drops oldest item)
recent = deque(maxlen=3)
for x in range(6):
    recent.append(x)
print(list(recent))   # [3, 4, 5]
```

## OrderedDict

In Python 3.7+ regular dicts preserve insertion order. `OrderedDict` is still useful when you need `move_to_end` or equality that considers order:

```python
from collections import OrderedDict

od = OrderedDict()
od["a"] = 1
od["b"] = 2
od.move_to_end("a")          # move to last
od.move_to_end("b", last=False)   # move to first
```

## namedtuple

Creates lightweight, immutable record types without defining a full class.

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)    # 3 4
print(p)           # Point(x=3, y=4)
print(p._asdict()) # {'x': 3, 'y': 4}

# Useful for returning multiple values from a function
Stat = namedtuple("Stat", "min max mean")
def summarise(xs):
    return Stat(min(xs), max(xs), sum(xs)/len(xs))
```

For mutable records with defaults and type annotations, prefer `dataclasses.dataclass` instead.

## ChainMap

Combines multiple dicts into a single view. Lookups check dicts left to right; writes go to the first map only.

```python
from collections import ChainMap

defaults = {"color": "red", "size": 10}
overrides = {"color": "blue"}
config = ChainMap(overrides, defaults)

print(config["color"])   # "blue"  (from overrides)
print(config["size"])    # 10      (from defaults)
```

Handy for layered configuration (command line → env vars → file → defaults).

## Quick reference

| Type | Use for |
|------|---------|
| `Counter` | Counting / frequency analysis |
| `defaultdict` | Grouping / graph adjacency lists |
| `deque` | Queues, stacks, sliding windows |
| `namedtuple` | Lightweight immutable records |
| `OrderedDict` | LRU caches, ordered maps |
| `ChainMap` | Layered config / scope lookups |
