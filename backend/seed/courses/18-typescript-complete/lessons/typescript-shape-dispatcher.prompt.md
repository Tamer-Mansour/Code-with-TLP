# Type-Safe Shape Dispatcher

A **discriminated union** is a union of object types where each member has a unique literal field called the *discriminant*. This pattern is the foundation of safe branching in TypeScript: a `switch` on the discriminant narrows each case to exactly that variant's properties.

## Problem

Read shape descriptions from stdin. Each line is:

```
<shape_type> <param1> [param2]
```

Supported shapes:

| Shape | Parameters |
|---|---|
| `circle` | `radius` |
| `rectangle` | `width height` |
| `triangle` | `base height` |

For each line, compute the area and print it rounded to **2 decimal places**.

Formulas:
- Circle: `π × radius²`
- Rectangle: `width × height`
- Triangle: `0.5 × base × height`

## Input

Multiple lines, one shape per line. Blank lines should be ignored.

## Output

One number per line, rounded to 2 decimal places.

## Example

**Input:**
```
circle 5
rectangle 4 6
triangle 3 8
circle 2.5
rectangle 10 3
```

**Output:**
```
78.54
24.00
12.00
19.63
30.00
```

## TypeScript connection

In TypeScript you would model this as:

```ts
type Shape =
  | { kind: "circle";    radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle";  base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":    return Math.PI * s.radius ** 2;
    case "rectangle": return s.width * s.height;
    case "triangle":  return 0.5 * s.base * s.height;
  }
}
```

Inside each `case`, TypeScript narrows `s` to only the matching variant — `s.radius` is only available in the `"circle"` branch. Your solution simulates this dispatch logic.
