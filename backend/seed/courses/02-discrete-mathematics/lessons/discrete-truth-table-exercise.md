# Exercise: Truth Table Generator

Propositional logic is the foundation of digital circuits, programming language semantics, and formal verification. In this exercise you will evaluate the five core logical connectives for a given pair of Boolean inputs.

A **truth table** lists every possible combination of input values alongside the resulting output values for each compound proposition. With two variables there are exactly four rows. Here you focus on a single row — the one given by the input.

## The Five Connectives

| Connective | Symbol | Rule |
|------------|--------|------|
| AND | p ∧ q | True only when both are true |
| OR | p ∨ q | True when at least one is true |
| NOT p | ¬p | True when p is false |
| IMPLIES | p → q | False only when p is true and q is false |
| IFF | p ↔ q | True when p and q share the same value |

### Critical correctness note

`p IMPLIES q` is **vacuously true** whenever p is false — this is one of the most common logic errors. The only case where `p → q` is false is `p = 1, q = 0`.

### Python encoding

```python
implies = (1 - p) | q       # (NOT p) OR q
iff     = implies & ((1 - q) | p)
```

Read the problem statement for full details on input format and expected output lines.
