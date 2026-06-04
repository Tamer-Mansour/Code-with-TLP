# Type Coercion Oracle

## Problem

You are given N JavaScript expressions. For each one, output the result as JavaScript would evaluate it.

**Supported expression forms:**

1. `typeof X` — output the string JavaScript's `typeof` operator returns for X
2. `A == B` — output `true` or `false` per JavaScript's loose equality rules
3. `A === B` — output `true` or `false` per JavaScript's strict equality rules

**typeof reference:**

| Value | typeof result |
|-------|--------------|
| null | object |
| undefined | undefined |
| NaN | number |
| 42 | number |
| hello | string |
| true / false | boolean |
| [] | object |
| {} | object |

**Key equality rules:**

- `NaN == NaN` → `false` (NaN never equals anything, including itself)
- `null == undefined` → `true` (only these two loosely equal each other; `null == 0` is `false`)
- `0 == false` → `true`
- `'' == false` → `true`
- `0 == ''` → `true`
- Strict equality (`===`) never coerces: different types → `false`

## Input Format

```
N
expression
...
```

- Line 1: N (1 ≤ N ≤ 50)
- Next N lines: one expression each

## Output Format

One result per line (a type string or `true`/`false`).

## Examples

**Input:**
```
6
typeof null
typeof NaN
NaN == NaN
null == undefined
null === undefined
0 == false
```

**Output:**
```
object
number
false
true
false
true
```

**Input:**
```
4
typeof undefined
typeof []
null == 0
0 == ''
```

**Output:**
```
undefined
object
false
true
```

## Constraints

- N ≤ 50
- All values and operands come from the sets defined above
