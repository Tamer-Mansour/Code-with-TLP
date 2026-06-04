# Exercise: Type-Safe Shape Dispatcher

Practice dispatching on a discriminated union by computing areas for different shape types read from stdin.

## What you will practice

- Parsing structured text input and branching by type
- The discriminated union pattern: one shared field narrows to a specific variant
- Exhaustive case handling

## Background

In TypeScript, a discriminated union gives each variant a unique literal field (the *discriminant*). A `switch` on that field narrows the type in each branch so you can only access fields that actually belong to that variant. This exercise simulates that pattern in code you can run and test.

## Instructions

Read lines from stdin. Each line is a shape description:

- `circle <radius>`
- `rectangle <width> <height>`
- `triangle <base> <height>`

Print the area of each shape, rounded to 2 decimal places, one per line.

See the prompt for the full specification, formulas, and examples.
