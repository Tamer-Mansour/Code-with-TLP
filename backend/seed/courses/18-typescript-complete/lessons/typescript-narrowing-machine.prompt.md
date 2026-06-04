# Type Narrowing State Machine

TypeScript's **control flow analysis** tracks which types are possible at each point in your code. When you write `if (typeof x === "string")`, TypeScript narrows the type of `x` to `string` in the true branch. Guards can be chained — each one further restricts the set of possible types.

## Problem

Each input line has the format:

```
<value> | <guard1> [guard2 ...]
```

Parse the value and apply each guard in order. If a guard excludes the value, output `never`. Otherwise output the final inferred type.

**Value formats:**

| Input token | Parsed type |
|---|---|
| `42`, `-3` (integer, no `.`) | `number` |
| `3.14`, `0.5` (contains `.`) | `number` |
| `true` or `false` | `boolean` |
| `null` | `null` |
| `undefined` | `undefined` |
| `"hello"` (double-quoted) | `string` |

**Guards:**

| Guard | Keeps the value if... |
|---|---|
| `typeof_string` | type is `string` |
| `typeof_number` | type is `number` |
| `typeof_boolean` | type is `boolean` |
| `not_null` | type is NOT `null` |
| `not_undefined` | type is NOT `undefined` |
| `is_finite` | type is `number` AND value is finite (not NaN, not Infinity) |

If a guard eliminates the value, stop applying further guards and print `never`.

## Input

Multiple lines. Each line: `<value> | <guards...>`

## Output

One line per input: the narrowed type name, or `never`.

## Example

**Input:**
```
42 | typeof_number
"hello" | typeof_string
null | not_null
true | typeof_boolean
3.14 | typeof_number is_finite
"world" | typeof_number
undefined | not_undefined
99 | typeof_number is_finite
```

**Output:**
```
number
string
never
boolean
number
never
never
number
```

## TypeScript connection

```ts
function process(x: string | number | null | undefined) {
  if (typeof x === "string") {
    // x: string — typeof_string guard applied
    return x.toUpperCase();
  }
  if (x !== null && x !== undefined) {
    // x: number — not_null + not_undefined applied
    return isFinite(x) ? x * 2 : 0;
  }
  // x: null | undefined — no guards passed
}
```

TypeScript performs this narrowing statically. Your solution models the same logic at runtime.
