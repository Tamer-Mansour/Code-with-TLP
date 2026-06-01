# Lists and Tuples

## Lists — mutable ordered sequences

```python
xs = [1, 2, 3]
xs.append(4)              # [1,2,3,4]
xs.extend([5, 6])         # [1,2,3,4,5,6]
xs.insert(0, 0)           # [0,1,2,3,4,5,6]
xs.pop()                  # returns 6, xs is [0..5]
xs.pop(0)                 # returns 0, xs is [1..5]
xs.remove(3)              # removes first 3
xs.reverse()
xs.sort()
xs.sort(key=abs, reverse=True)
```

Index from the back with negatives: `xs[-1]` is the last.

### Slicing

```python
xs[1:4]          # indices 1, 2, 3
xs[:3]           # first three
xs[3:]           # from index 3 to end
xs[::2]          # every other element
xs[::-1]         # reversed copy
```

Slicing returns a **new list**. Assignment to a slice mutates in place:

```python
xs[1:3] = [10, 20, 30]    # replaces 2 items with 3
```

### Common patterns

```python
"any of these truthy?":  any(predicate(x) for x in xs)
"all of these truthy?":  all(predicate(x) for x in xs)
"how many match?":       sum(1 for x in xs if predicate(x))
"unique?":               list(set(xs))   # loses order
"unique preserving order": list(dict.fromkeys(xs))
"flatten one level":     [x for sub in xs for x in sub]
```

### Copying

```python
b = xs                   # both refer to the same list!
b = xs.copy()            # shallow copy
b = xs[:]                # also shallow copy
import copy
b = copy.deepcopy(xs)    # deep copy of nested structures
```

## Tuples — immutable ordered sequences

```python
point = (3, 4)
x, y = point             # unpacking
```

Tuples are used wherever you need a fixed-shape collection: function returns, dict keys, set members. Because they're immutable, they're **hashable** — lists aren't, so a list can never be a dict key.

```python
seen = {(0, 0), (1, 2)}        # set of points
distances = {(0, 0): 0, (1, 2): 2.24}
```

### Named tuples

```python
from collections import namedtuple
Point = namedtuple("Point", "x y")
p = Point(3, 4)
p.x, p.y                       # field access
```

For more, `dataclass(frozen=True)` is the modern, typed version.

### Single-element tuple

```python
t = (1,)        # comma is required
t = (1)         # this is just int 1 in parentheses
```

A surprisingly common Python footgun.

## When to use which

- Will I modify it? → **list**
- Is it a fixed record (point, RGB color)? → **tuple**
- Will it be a dict key or set member? → **tuple**
- Do I want field names? → **dataclass** (better than tuple for >2 fields)
