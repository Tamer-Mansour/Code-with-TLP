# Simplifying Logic with Karnaugh Maps

A **Karnaugh map (K-map)** is a graphical tool that arranges truth-table rows so that adjacent cells differ by exactly one variable — turning Boolean simplification into a visual pattern-matching exercise. It is faster and less error-prone than algebraic manipulation for up to 4–5 variables.

## Why K-Maps Work

The key insight: two adjacent cells that differ in only one variable allow the complement law to eliminate that variable.

```
A·B̄ + A·B = A·(B̄ + B) = A·1 = A
```

K-maps lay out cells so that every orthogonal neighbor satisfies this "differ by one" property, including wrap-around edges.

## 2-Variable K-Map

```
        B=0   B=1
  A=0 |  0  |  1  |
  A=1 |  2  |  3  |
```

Cells are numbered by minterm index (decimal equivalent of the binary address `AB`).

## 3-Variable K-Map

Columns use **Gray code** ordering (00 → 01 → 11 → 10) so adjacent columns differ by one bit:

```
          BC
      00  01  11  10
A=0 |  0 | 1 | 3 | 2 |
A=1 |  4 | 5 | 7 | 6 |
```

## 4-Variable K-Map (Most Common in Interviews)

```
           CD
       00   01   11   10
AB=00 | 0  | 1  | 3  | 2  |
AB=01 | 4  | 5  | 7  | 6  |
AB=11 | 12 | 13 | 15 | 14 |
AB=10 | 8  | 9  | 11 | 10 |
```

## Rules for Grouping

1. **Only group 1s** (for Sum-of-Products, SOP). Group 0s for Product-of-Sums (POS).
2. **Group sizes must be powers of 2**: 1, 2, 4, 8, 16 …
3. **Make groups as large as possible** — larger groups eliminate more variables.
4. **Groups can wrap around** edges (left↔right, top↔bottom).
5. **Every 1 must be covered** by at least one group.
6. **Minimize the number of groups** (each group = one product term in SOP).

## Worked Example

Truth table for `F(A,B,C,D)`:

| Minterm | A | B | C | D | F |
|---------|---|---|---|---|---|
| 0  | 0 | 0 | 0 | 0 | 1 |
| 1  | 0 | 0 | 0 | 1 | 1 |
| 2  | 0 | 0 | 1 | 0 | 0 |
| 3  | 0 | 0 | 1 | 1 | 1 |
| 4  | 0 | 1 | 0 | 0 | 1 |
| 5  | 0 | 1 | 0 | 1 | 1 |
| ... | | | | | |
| 12 | 1 | 1 | 0 | 0 | 1 |
| 13 | 1 | 1 | 0 | 1 | 1 |

Fill the K-map with 1s at minterms 0,1,3,4,5,12,13:

```
           CD
       00   01   11   10
AB=00 | 1  | 1  | 1  | 0  |
AB=01 | 1  | 1  | 0  | 0  |
AB=11 | 1  | 1  | 0  | 0  |
AB=10 | 0  | 0  | 0  | 0  |
```

Groups:
- **Group 1** (cells 0,1,4,5,12,13): A=0 or (AB=11), C=0 → this spans 6 cells — break it down: cells {0,1,4,5} (A=0, C=0) = `Ā·C̄`; cells {12,13} (AB=11, C=0) = `A·B·C̄`
- **Group 2** (cells 0,1,3): (A=0, B=0, C=0) then (0,1) = `Ā·B̄·C̄` plus (1,3)...

Simplified result (for the visible 1s): `F = Ā·C̄ + Ā·B̄·D + A·B·C̄`

## Don't-Care Conditions

Use `X` in cells where the input combination never occurs (e.g., unused BCD states 10–15). You may treat X as 0 or 1, whichever makes a group larger.

```
           CD
       00   01   11   10
AB=10 | X  | X  | X  | X  |   ← treat all as 1 to extend group
```

## Common Pitfalls

- **Non-power-of-2 groups**: a group of 3 or 5 is illegal; split it differently.
- **Forgetting wrap-around**: the left and right columns are adjacent; so are top and bottom rows.
- **Choosing minimal covering without redundancy check**: after covering all 1s, remove any group whose 1s are fully covered by other groups — this is an **essential prime implicant** check.

## Interview Answer

> "A K-map exploits Gray-code ordering to make algebraically adjacent minterms physically adjacent. You circle groups of 1s in powers of two, as large as possible, then read off the simplified product term by noting which variables remain constant across the group."
