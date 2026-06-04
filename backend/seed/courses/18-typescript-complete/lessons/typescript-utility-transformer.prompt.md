# Utility Type Transformer

TypeScript's built-in **utility types** transform existing types into new ones without repeating yourself. `Partial<T>` makes every property optional; `Required<T>` makes every property required; `Pick<T, K>` keeps only named keys; `Omit<T, K>` drops named keys.

## Problem

You are given a schema as a comma-separated list of `field:status` pairs on the first line, where status is either `required` or `optional`. Then a series of transformation commands follow.

**Schema format (line 1):**
```
name:required,age:required,email:optional,role:optional
```

**Commands:**

| Command | Output |
|---|---|
| `PARTIAL` | All fields (Partial makes everything optional — every field survives) |
| `REQUIRED` | Only the originally-required fields |
| `PICK <f1> <f2> ...` | Only the named fields, in their original schema order |
| `OMIT <f1> <f2> ...` | All fields except the named ones, in original schema order |

For each command, print the resulting field names as a comma-separated list in **original schema order**.

## Input

```
<schema>
<COMMAND [args]>
<COMMAND [args]>
...
```

## Output

One comma-separated line per command.

## Example

**Input:**
```
name:required,age:required,email:optional,role:optional
PARTIAL
REQUIRED
PICK name role
OMIT age email
```

**Output:**
```
name,age,email,role
name,age
name,role
name,role
```

## TypeScript connection

```ts
interface Profile {
  name: string;
  age: number;
  email?: string;
  role?: string;
}

type AllOptional = Partial<Profile>;
// { name?: string; age?: number; email?: string; role?: string }

type NameAndRole = Pick<Profile, "name" | "role">;
// { name: string; role?: string }

type WithoutAge = Omit<Profile, "age">;
// { name: string; email?: string; role?: string }
```

These utility types are implemented using mapped types internally: `Partial<T>` is `{ [K in keyof T]?: T[K] }`. Your solution models the same key-filtering logic.
