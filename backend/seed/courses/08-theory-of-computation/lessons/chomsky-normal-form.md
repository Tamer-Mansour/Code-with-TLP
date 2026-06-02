# Chomsky Normal Form

**Chomsky Normal Form (CNF)** is a restricted form of context-free grammar where every production rule has one of exactly two shapes:

1. **Binary rule:** A → BC (variable produces two variables)
2. **Terminal rule:** A → a (variable produces one terminal)

Plus, optionally, **S → ε** if the start symbol S generates the empty string (but only the start symbol may have an ε-rule in CNF).

Any CFG that does not generate ε (or generates ε only from the start variable) can be converted to CNF. This normal form is the input requirement for the **CYK algorithm** and simplifies many theoretical proofs.

## Why CNF Matters

- The CYK membership algorithm requires CNF: its dynamic programming recurrence splits the string into two parts and asks which variables derive each part.
- CNF makes the parse-tree structure binary and of depth ≤ 2|w| − 1, giving clean complexity bounds.
- Many proofs about CFLs (e.g., the CFL pumping lemma) are easier to state over CNF grammars.

## The Four-Step Conversion

Given a CFG G, convert to CNF in this order:

### Step 1 — Add a new start variable

Introduce a new start variable S₀ with rule S₀ → S. This ensures the original S can appear on the right-hand side without violating CNF restrictions.

### Step 2 — Eliminate ε-productions (A → ε for A ≠ S₀)

Find every **nullable** variable (one that can derive ε). For each production containing a nullable variable A, add a copy of the rule with A removed. Repeat until no new nullables are found.

```
Example: if A → ε and B → uAv, add B → uv.
If both A and B are nullable and C → AB, add C → A, C → B, C → ε (but remove C → ε later if C ≠ S₀).
```

Remove all ε-productions A → ε (except S₀ → ε if needed).

### Step 3 — Eliminate unit rules (A → B)

A **unit rule** is a production A → B where B is a single variable. Find the unit closure: if A ⇒* B by unit rules and B → u is a non-unit rule, add A → u directly. Then remove all unit rules.

```
Example: if A → B and B → C and C → ab, add A → ab and A → C → ab path.
```

### Step 4 — Binarize long rules and isolate terminals

For any rule with two or more symbols on the right:

- **Replace terminals inside long rules** with fresh variables: if the rule is A → aB, introduce Tₐ → a and rewrite as A → Tₐ B.
- **Break long rules into binary rules**: A → B₁B₂B₃ becomes A → B₁A₁ and A₁ → B₂B₃ using a fresh variable A₁.

## Worked Example

Original grammar for { aⁿbⁿ | n ≥ 1 }:

```
S → aSb | ab
```

**After Step 1:** S₀ → S, S → aSb | ab

**After Step 2:** No ε-productions (the language does not contain ε). No changes.

**After Step 3:** No unit rules. No changes.

**After Step 4 — Isolate terminals and binarize:**

Rule `S → aSb`:
- Introduce Tₐ → a and T_b → b.
- Rewrite: S → Tₐ S₁ where S₁ → S T_b

Rule `S → ab`:
- Rewrite: S → Tₐ T_b

Final CNF grammar:

```
S₀ → S
S  → Tₐ S₁  |  Tₐ T_b
S₁ → S T_b
Tₐ → a
T_b → b
```

Verify that `aabb` is derived:

```
S ⇒ Tₐ S₁ ⇒ a S₁ ⇒ a (S T_b) ⇒ a (Tₐ T_b) T_b ⇒ a a b b  ✓
```

## Grammar Size After Conversion

| Grammar property | Before CNF | After CNF |
|-----------------|------------|-----------|
| Number of variables | V | O(V + R) |
| Number of rules | R | O(V · R) |
| Parse tree depth | variable | ≤ 2|w| − 1 |

The blow-up is at most polynomial, so CNF conversion does not change the decidability or complexity of the membership problem — it only affects constant factors.

## Key Takeaways

- CNF forces all rules into exactly two shapes, enabling clean inductive proofs and the CYK dynamic programming algorithm.
- The four-step procedure always terminates and produces an equivalent grammar (same language, except possibly ε).
- Every CFL has a CNF grammar; this is a fundamental structural fact about context-free languages.
