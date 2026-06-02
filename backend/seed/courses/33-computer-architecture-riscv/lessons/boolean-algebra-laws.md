# Boolean Algebra Laws and Identities

Boolean algebra gives us a formal system to manipulate logic expressions symbolically — the same way ordinary algebra lets you simplify `2x + 3x` to `5x`. Mastering these laws lets you minimize gate counts, reduce power consumption, and reason about hardware correctness without drawing a single wire.

## Variables and Constants

In Boolean algebra every variable is either **0** (false) or **1** (true). Operations are:

- **AND** (`·`): multiplication analogy
- **OR** (`+`): addition analogy
- **NOT** (`‾`): complement

## Fundamental Laws

### Identity Laws
```
A + 0 = A        (OR with 0 changes nothing)
A · 1 = A        (AND with 1 changes nothing)
```

### Null (Dominance) Laws
```
A + 1 = 1        (OR with 1 always gives 1)
A · 0 = 0        (AND with 0 always gives 0)
```

### Idempotent Laws
```
A + A = A
A · A = A
```

### Complement Laws
```
A + Ā = 1        (a variable OR its complement = 1)
A · Ā = 0        (a variable AND its complement = 0)
```

### Involution (Double Negation)
```
¬(¬A) = A
```

### Commutative Laws
```
A + B = B + A
A · B = B · A
```

### Associative Laws
```
(A + B) + C = A + (B + C)
(A · B) · C = A · (B · C)
```

### Distributive Laws
```
A · (B + C) = (A · B) + (A · C)   ← AND distributes over OR
A + (B · C) = (A + B) · (A + C)   ← OR distributes over AND  ← often forgotten!
```

### Absorption Laws
```
A + (A · B) = A
A · (A + B) = A
```
These are gate-count gold: an absorbed term disappears entirely.

### De Morgan's Theorems

The most important identities in digital design:

```
¬(A · B) = Ā + B̄      (NAND = NOR of complements)
¬(A + B) = Ā · B̄      (NOR  = NAND of complements)
```

**Practical rule**: "Break the bar, change the sign." To negate an expression, complement each variable and swap AND↔OR.

## Worked Example: Simplifying a Sum-of-Products

Given: `F = A·B̄·C + A·B·C + A·B̄·C̄`

Step 1 — factor out `A·B̄` from terms 1 and 3:
```
F = A·B̄·(C + C̄) + A·B·C
  = A·B̄·1       + A·B·C        (complement law)
  = A·B̄          + A·B·C        (identity law)
```

Step 2 — factor out `A`:
```
F = A·(B̄ + B·C)
```

Step 3 — apply the second distributive law (`X + Y·Z = (X+Y)·(X+Z)`) in reverse, or use absorption. Notice `B̄ + B·C = B̄ + C` (a standard identity):
```
F = A·(B̄ + C)
```

That reduced **3 AND gates + 1 OR gate** down to **1 AND gate + 1 OR gate + 1 NOT gate**.

## Consensus Theorem

```
A·B + Ā·C + B·C = A·B + Ā·C
```

The third term `B·C` is redundant — it is always covered by one of the first two terms. Spotting consensus terms is a key skill in Karnaugh-map simplification.

## Common Pitfalls

- **Forgetting the second distributive law**: most engineers memorize AND-over-OR but forget OR-over-AND, which trips them up with sums of products.
- **Misapplying De Morgan**: the bar must cover the entire expression. `¬A·¬B ≠ ¬(A·B)`.
- **Skipping absorption**: a term like `X + X·Y` is just `X`; leaving it in wastes gates.

## Interview Answer

> "Boolean algebra provides a closed set of laws — identity, complement, De Morgan, distributive — that let you algebraically reduce a logic expression to its minimal form before committing to hardware. De Morgan's theorems are especially critical because they show how NAND and NOR relate to AND/OR, enabling all-NAND or all-NOR implementations."
