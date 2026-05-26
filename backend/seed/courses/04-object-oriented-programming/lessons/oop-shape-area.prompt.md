# Shape Area Calculator

Implement a shape hierarchy with a base class `Shape` and subclasses `Circle`, `Rectangle`, and `Triangle`. Then process commands to create shapes and compute their areas.

## Commands

- `CIRCLE <radius>` — create a Circle with the given radius
- `RECTANGLE <width> <height>` — create a Rectangle with the given dimensions
- `TRIANGLE <base> <height>` — create a Triangle with the given base and height
- `AREA` — print the area of the most recently created shape, rounded to 2 decimal places

## Formulas

- Circle: `area = 3.14159 * radius^2`
- Rectangle: `area = width * height`
- Triangle: `area = 0.5 * base * height`

## Input Format

The first line is an integer `N` — the number of commands.
The next `N` lines each contain one command.

All dimensions are positive integers.

## Output Format

For each `AREA` command, print the area of the current shape on its own line, formatted to exactly 2 decimal places.

## Example

**Input:**
```
6
CIRCLE 5
AREA
RECTANGLE 4 6
AREA
TRIANGLE 3 8
AREA
```

**Output:**
```
78.54
24.00
12.00
```
