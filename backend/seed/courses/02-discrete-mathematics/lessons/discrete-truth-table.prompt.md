# Truth Table Generator

## Problem

Given two Boolean variables `p` and `q` (each either `0` or `1`), evaluate and print the results of the five core propositional-logic connectives:

1. `p AND q`
2. `p OR q`
3. `NOT p`
4. `p IMPLIES q` — defined as `(NOT p) OR q`
5. `p IFF q` — defined as `(p IMPLIES q) AND (q IMPLIES p)`

## Input Format

A single line with two space-separated integers: `p q` (each is `0` or `1`).

## Output Format

Five lines, each in the format `<name>: <value>` where value is `0` or `1`.

```
p AND q: <val>
p OR q: <val>
NOT p: <val>
p IMPLIES q: <val>
p IFF q: <val>
```

## Constraints

- `p ∈ {0, 1}`, `q ∈ {0, 1}`

## Examples

| Input | Output |
|-------|--------|
| `1 0` | `p AND q: 0`<br>`p OR q: 1`<br>`NOT p: 0`<br>`p IMPLIES q: 0`<br>`p IFF q: 0` |
| `0 0` | `p AND q: 0`<br>`p OR q: 0`<br>`NOT p: 1`<br>`p IMPLIES q: 1`<br>`p IFF q: 1` |
| `1 1` | `p AND q: 1`<br>`p OR q: 1`<br>`NOT p: 0`<br>`p IMPLIES q: 1`<br>`p IFF q: 1` |

## Key Insight

`p IMPLIES q` is **false only when p is 1 and q is 0**. When p is 0, the implication is vacuously true regardless of q. This is the most commonly misunderstood connective in introductory logic.

## Hint

Represent `IMPLIES` as `(1 - p) | q` and `IFF` as `implies & ((1 - q) | p)`.
