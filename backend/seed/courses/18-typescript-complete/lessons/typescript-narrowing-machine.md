# Exercise: Type Narrowing State Machine

Apply a chain of type guards to values and determine the narrowed type — or `never` if a guard eliminates the value entirely.

## What you will practice

- Understanding TypeScript's control flow analysis
- Applying type guards in sequence: each guard reduces the possible type set
- Recognising when a value is narrowed to `never`

## Background

TypeScript tracks types through branches. Each guard (`typeof`, `!== null`, `!== undefined`) is a *type predicate* that narrows the variable's type in the branches where it holds. Chaining guards narrows further: after `typeof x === "number"` and `isFinite(x)`, TypeScript knows `x` is a finite number.

The `never` type represents an impossible value — a variable narrowed to `never` means no code in that branch can ever run. This is what makes exhaustiveness checking work: if you handle every case of a union, the default branch sees `never`.

## Instructions

Each line of input has a value and a sequence of guards separated by `|`. Apply the guards in order to determine the surviving type. Print `never` if any guard eliminates the value.

See the prompt for the full value format, guard definitions, and worked example.
