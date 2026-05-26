# Propositions and Connectives

A **proposition** is a declarative statement that is either true or false — never both, never neither. This property is called **bivalence**, and it is the bedrock assumption of classical (Boolean) logic. For example, "7 is prime" is a proposition (it is true), "17 + 3 = 21" is a proposition (it is false), while "What time is it?" is not a proposition because it does not assert anything.

Propositions are the atoms from which all logical reasoning is built. In computer science, every Boolean expression in your code — `if x > 0 and not flag` — is a compound proposition. Understanding their structure lets you simplify conditions, eliminate bugs, and reason formally about programs.

## Atomic vs. Compound Propositions

The simplest propositions are called **atomic** — they contain no logical connectives. We denote them with lowercase letters: `p`, `q`, `r`, …

- `p` : "It is raining."
- `q` : "The road is wet."

Compound propositions are built by connecting atoms with **logical connectives**.

## The Five Core Connectives

| Symbol | Name | Read as | True when… |
|--------|------|---------|------------|
| `¬p` | Negation | "not p" | p is false |
| `p ∧ q` | Conjunction | "p and q" | both p and q are true |
| `p ∨ q` | Disjunction | "p or q" | at least one is true |
| `p → q` | Implication | "if p then q" | p is false, OR q is true |
| `p ↔ q` | Biconditional | "p if and only if q" | p and q have the same truth value |

### Notation notes

- Conjunction `∧` maps directly to `&&` (C, Java, Python's `and`).
- Disjunction `∨` maps to `||` (`or`).
- Negation `¬` maps to `!` (`not`).
- Implication `→` has no direct programming operator but appears everywhere in specifications and proofs.

## Truth Tables

A **truth table** enumerates every possible combination of truth values. For n variables there are `2^n` rows.

```
p   q  | ¬p  | p∧q | p∨q | p→q | p↔q
---------------------------------------------
T   T  |  F  |  T  |  T  |  T  |  T
T   F  |  F  |  F  |  T  |  F  |  F
F   T  |  T  |  F  |  T  |  T  |  F
F   F  |  T  |  F  |  F  |  T  |  T
```

With three variables (p, q, r) you would need `2^3 = 8` rows, and so on.

### The Implication Trap

`p → q` is **false only when p is true and q is false**. This surprises many students. Think of it as a promise: "If you score 90+, you get an A." The only **broken** promise is scoring 90+ and not receiving an A. If you score below 90, the promise says nothing — it is vacuously satisfied regardless of the grade outcome.

This explains two CS idioms:
- "Vacuous truth": `False → anything` is always true. A function that never gets called can never break its contract.
- Precondition reasoning: if a function's precondition is false, its postcondition holds trivially.

## Logical Equivalence

Two formulas are **logically equivalent** (`≡`) if they have identical truth values for every assignment. We verify equivalence by building truth tables and comparing the final columns.

### De Morgan's Laws

De Morgan's Laws show how negation distributes through conjunction and disjunction:

```
¬(p ∧ q) ≡ ¬p ∨ ¬q
¬(p ∨ q) ≡ ¬p ∧ ¬q
```

**Worked verification of `¬(p ∧ q) ≡ ¬p ∨ ¬q`:**

```
p   q  | p∧q | ¬(p∧q) | ¬p  | ¬q  | ¬p ∨ ¬q
------------------------------------------------
T   T  |  T  |   F    |  F  |  F  |    F
T   F  |  F  |   T    |  F  |  T  |    T
F   T  |  F  |   T    |  T  |  F  |    T
F   F  |  F  |   T    |  T  |  T  |    T
```

Columns 4 and 7 are identical. QED.

**CS application:** In Python, `not (a > 0 and b > 0)` is equivalent to `not a > 0 or not b > 0`, i.e., `a <= 0 or b <= 0`. Compilers use De Morgan's Laws for branch optimizations.

### Other Important Equivalences

| Law | Formula |
|-----|---------|
| Double Negation | `¬¬p ≡ p` |
| Contrapositive | `p → q ≡ ¬q → ¬p` |
| Implication as disjunction | `p → q ≡ ¬p ∨ q` |
| Biconditional expansion | `p ↔ q ≡ (p → q) ∧ (q → p)` |
| Idempotent | `p ∧ p ≡ p`, `p ∨ p ≡ p` |
| Absorption | `p ∧ (p ∨ q) ≡ p` |
| Distributive | `p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)` |

### Worked Example: Contrapositive

Show `p → q ≡ ¬q → ¬p`:

```
p   q  | p→q | ¬q  | ¬p  | ¬q→¬p
------------------------------------
T   T  |  T  |  F  |  F  |   T
T   F  |  F  |  T  |  F  |   F
F   T  |  T  |  F  |  T  |   T
F   F  |  T  |  T  |  T  |   T
```

Columns 3 and 6 are identical. The contrapositive is the logical basis for **proof by contrapositive** — if proving `p → q` is hard, you can instead prove `¬q → ¬p`, which is often easier.

## Tautologies, Contradictions, and Satisfiability

- A **tautology** is always true for every assignment (e.g., `p ∨ ¬p`). In hardware design, a tautological output means the circuit can be eliminated.
- A **contradiction** is always false (e.g., `p ∧ ¬p`). A contradictory requirement means the specification is inconsistent.
- A **contingency** depends on the variable values — it is neither always true nor always false.
- A formula is **satisfiable** if at least one assignment makes it true. The Boolean Satisfiability Problem (SAT) — given a compound proposition, is it satisfiable? — is the canonical NP-complete problem.

## Operator Precedence

When parentheses are omitted, evaluate in this order (highest to lowest):

1. `¬` (negation)
2. `∧` (conjunction)
3. `∨` (disjunction)
4. `→` (implication, right-associative)
5. `↔` (biconditional)

So `¬p ∨ q → r` parses as `(¬p ∨ q) → r`, and `p → q → r` parses as `p → (q → r)`.

## Normal Forms

Any compound proposition can be rewritten in a **normal form**, which is useful for automated reasoning.

### Conjunctive Normal Form (CNF)

A conjunction (`∧`) of **clauses**, where each clause is a disjunction (`∨`) of literals (atomic propositions or their negations).

Example: `(p ∨ ¬q) ∧ (¬p ∨ r) ∧ q`

SAT solvers (used in verification tools, AI planning, compilers) work on CNF. Converting to CNF uses De Morgan's Laws and distributivity.

### Disjunctive Normal Form (DNF)

A disjunction of **minterms**, where each minterm is a conjunction of literals.

Example: `(p ∧ q) ∨ (¬p ∧ r)`

DNF directly encodes the rows of a truth table that produce `T`.

## Common Pitfalls

| Mistake | Correct understanding |
|---------|----------------------|
| `p → q` is the same as `q → p` | These are **converses** and not logically equivalent |
| `p → q` is false when p is false | It is **vacuously true** when p is false |
| Negating `p → q` gives `¬p → ¬q` | The negation is `p ∧ ¬q` |
| Exclusive or (`XOR`) is the same as `∨` | XOR (`p ⊕ q`) is true when exactly one is true; `∨` allows both |

## Key Takeaways

- Every proposition is either **T** (true) or **F** (false).
- The five main connectives are negation, conjunction, disjunction, implication, and biconditional.
- Implication is false **only** when the hypothesis is true and the conclusion is false.
- De Morgan's Laws, the contrapositive, and the implication-as-disjunction identity are essential tools for simplifying and proving logical statements.
- SAT (propositional satisfiability) is the foundational NP-complete problem, making logic directly relevant to complexity theory.
