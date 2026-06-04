# Vector Class with Dunder Methods

## Problem Statement

Implement a `Vector` class representing a 2D vector with components `x` and `y` (integers).

**Required methods:**

- `__init__(self, x, y)` — stores `x` and `y`.
- `__repr__(self)` — returns `"Vector(x, y)"` (using the integer values, no spaces around the comma).
- `__add__(self, other)` — returns a new `Vector` whose components are the element-wise sum.
- `__eq__(self, other)` — returns `True` if both `x` and `y` match, `False` otherwise.
- `magnitude(self)` — returns `round(math.sqrt(x**2 + y**2), 4)` as a float.

**Input format:**

Read lines from stdin until EOF. Each line is one of:

| Command | Action |
|---------|--------|
| `add <x1> <y1> <x2> <y2>` | Print `repr(Vector(x1,y1) + Vector(x2,y2))` |
| `eq <x1> <y1> <x2> <y2>` | Print `Vector(x1,y1) == Vector(x2,y2)` |
| `mag <x> <y>` | Print `Vector(x,y).magnitude()` |

All component values are integers.

**Output format:**

- `add`: one line, the `repr` string of the resulting vector.
- `eq`: one line, `True` or `False`.
- `mag`: one line, the magnitude as a float (Python's default float printing is fine; `5.0` not `5.0000`).

## Examples

**Example 1**

Input:
```
add 1 2 3 4
eq 1 2 1 2
eq 1 2 3 4
mag 3 4
```

Output:
```
Vector(4, 6)
True
False
5.0
```

**Example 2**

Input:
```
add 0 0 0 0
eq 0 0 0 0
mag 0 0
```

Output:
```
Vector(0, 0)
True
0.0
```

**Example 3**

Input:
```
add 5 5 5 5
mag 5 12
eq 3 4 4 3
```

Output:
```
Vector(10, 10)
13.0
False
```

**Example 4**

Input:
```
mag 1 1
eq 2 3 2 3
add 10 20 30 40
```

Output:
```
1.4142
True
Vector(40, 60)
```

## Constraints

- Number of commands: 1 – 100
- Component values: −1000 ≤ x, y ≤ 1000
- You may use the `math` module from the standard library
