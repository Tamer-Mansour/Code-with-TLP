# Exercise: Generic Stack Simulator

Implement a stack simulator that responds to PUSH, POP, PEEK, and SIZE commands — modelling how TypeScript's generic `Stack<T>` works with full type safety.

## What you will practice

- Simulating a generic data structure
- Handling empty-collection edge cases
- Understanding why generics preserve type relationships

## Background

A `Stack<T>` in TypeScript is the canonical example of a generic class. The type parameter `T` flows through every operation: what you push is what you get back from pop and peek — the compiler enforces this. This exercise strips away the TypeScript syntax and asks you to implement the same logic in pure algorithmic form.

## Instructions

Read commands from stdin and execute them on an integer stack:

- `PUSH <value>` — push onto the stack (no output)
- `POP` — print and remove the top item, or `EMPTY`
- `PEEK` — print the top item without removing it, or `EMPTY`
- `SIZE` — print the current number of items

See the prompt for the complete specification and worked example.
