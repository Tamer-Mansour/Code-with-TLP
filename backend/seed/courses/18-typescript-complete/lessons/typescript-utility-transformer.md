# Exercise: Utility Type Transformer

Simulate the behaviour of TypeScript's `Partial`, `Required`, `Pick`, and `Omit` utility types on a schema of field definitions.

## What you will practice

- Understanding what each utility type does to the set of keys
- Preserving insertion order while filtering
- Translating TypeScript type-level operations into runtime logic

## Background

TypeScript ships with a set of built-in utility types that transform type shapes. They are implemented using mapped types under the hood, but you can understand them by their key-selection rules:

- `Partial<T>` — every key of T survives (all become optional)
- `Required<T>` — every key of T survives (all become required)
- `Pick<T, K>` — only the keys in K survive
- `Omit<T, K>` — all keys except those in K survive

This exercise asks you to apply those same filtering rules to a text-based schema.

## Instructions

Read a schema definition on the first line (comma-separated `field:required|optional` pairs), then execute PARTIAL, REQUIRED, PICK, and OMIT commands, printing the resulting field names for each.

See the prompt for the full specification, command reference, and worked example.
