# Interface Dispatch Table

## Problem

Go interfaces are satisfied implicitly — no `implements` keyword needed. A type satisfies an interface as soon as it defines all required methods with matching signatures.

This exercise simulates polymorphic dispatch through a `Shape` interface with one method: `Area() float64`. Three concrete types implement it:

- **CIRCLE** with radius `r`: area = π × r²
- **RECTANGLE** with width `w` and height `h`: area = w × h
- **TRIANGLE** with base `b` and height `h`: area = 0.5 × b × h

Use π = 3.141592653589793.

For each shape, compute its area and print it rounded to **2 decimal places**.

## Input Format

```
N
TYPE param1 [param2]
...
```

- Line 1: `N`, number of shapes (1 <= N <= 100)
- Next N lines: shape type followed by its parameters
  - `CIRCLE r` — one parameter (radius)
  - `RECTANGLE w h` — two parameters (width, height)
  - `TRIANGLE b h` — two parameters (base, height)

All parameters are positive real numbers.

## Output Format

N lines, one area per line, rounded to 2 decimal places.

## Example

**Input:**
```
4
CIRCLE 7
RECTANGLE 4 5
TRIANGLE 6 8
CIRCLE 3
```

**Output:**
```
153.94
20.00
24.00
28.27
```

## Constraints

- 1 <= N <= 100
- All dimensions are positive floats
- Use `math.Pi` (Python: `math.pi`) for π
