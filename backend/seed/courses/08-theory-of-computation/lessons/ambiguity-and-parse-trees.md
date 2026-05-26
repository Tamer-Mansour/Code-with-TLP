# Ambiguity and Parse Trees

A grammar is **ambiguous** if some string has two or more distinct parse trees, meaning it can be "understood" in two different ways. Ambiguity is a critical issue in programming language design and parsing — an ambiguous grammar for a programming language means that a program can be interpreted in multiple ways, producing different results.

## Formal Definitions

A CFG G is **ambiguous** if there exists w ∈ L(G) with two distinct **leftmost derivations** from S (equivalently, two distinct parse trees with yield w).

A language L is **inherently ambiguous** if every CFG for L is ambiguous. Such languages exist and cannot be disambiguated by any grammar rewriting.

## Detailed Example: Ambiguous Arithmetic Grammar

Consider:
```
E → E + E | E * E | (E) | id
```

The string `id + id * id` has **two** parse trees:

**Parse Tree 1** (+ is the root operator, (\*) below):
```
        E
      / | \
     E  +  E
     |    / | \
     id  E  *  E
         |     |
         id    id
```
This corresponds to `id + (id * id)` — multiply first, then add.

**Parse Tree 2** (\* is the root operator, (+) below):
```
        E
      / | \
     E  *  E
   / | \   |
  E  +  E  id
  |     |
  id    id
```
This corresponds to `(id + id) * id` — add first, then multiply.

These give different numeric results when `id` is a number (e.g., with id=2: Tree 1 gives 2+(2*2)=6, Tree 2 gives (2+2)*2=8). The grammar is ambiguous.

## Unambiguous Arithmetic Grammar

The standard fix encodes operator precedence and left-associativity:

```
E → E + T | T       -- addition (lowest precedence, left-associative)
T → T * F | F       -- multiplication (higher precedence, left-associative)
F → (E) | id        -- atomic (highest precedence)
```

Now `id + id * id` has a **unique** parse tree:

```
      E
    / | \
   E  +  T
   |    / | \
   T   T  *  F
   |   |     |
   F   F     id
   |   |
   id  id
```

Yield: id + (id * id). The unique leftmost derivation is:
```
E ⇒ E + T ⇒ T + T ⇒ F + T ⇒ id + T ⇒ id + T * F ⇒ id + F * F ⇒ id + id * F ⇒ id + id * id
```

The key structural insight: T appears as the right child of `+` in E → E + T, so any multiplicative sub-expression binds tighter than the surrounding addition. Similarly, E → E + T makes `+` left-associative: `a + b + c` parses as `(a + b) + c`.

## Inherently Ambiguous Languages

Some CFLs cannot be given any unambiguous grammar:

**Theorem.** The language L = {aⁱbʲcᵏ \| i = j or j = k, i,j,k ≥ 1} is inherently ambiguous.

*Intuition:* L is the union of L₁ = {aⁿbⁿcᵏ} (equal a's and b's) and L₂ = {aᵐbⁿcⁿ} (equal b's and c's). Any grammar for L must somehow generate both. The strings in L₁ ∩ L₂ = {aⁿbⁿcⁿ} can be derived via the L₁ mechanism or the L₂ mechanism — two different parse trees — and this ambiguity is unavoidable.

Inherently ambiguous languages cannot be parsed by deterministic methods (LL or LR). They require general algorithms like Earley's or CYK.

## Parsing Algorithms and Grammar Classes

| Parser | Grammar class | Time | Direction |
|--------|--------------|------|-----------|
| Recursive descent | LL(1) | O(n) | Top-down |
| LL(k) parser | LL(k) | O(n) | Top-down |
| LR(0), SLR(1), LALR(1) | Various subsets of unambiguous CFGs | O(n) | Bottom-up |
| LR(1) / canonical LR | Larger deterministic subsets | O(n) | Bottom-up |
| Earley's algorithm | All CFGs (including ambiguous) | O(n³) / O(n²) for unambiguous | Top-down dynamic programming |
| CYK | CFGs in CNF | O(n³·\|G\|) | Bottom-up dynamic programming |

Most programming languages are designed to have LR(1) grammars, enabling efficient O(n) parsing by LR parsers. The dangling-else ambiguity in C/Pascal is a classic example of a problematic case resolved by a language-level disambiguation rule ("else binds to the nearest if").

## The Ambiguity of the Dangling Else

Consider the grammar fragment:
```
Stmt → if E then Stmt
     | if E then Stmt else Stmt
     | other
```

The string `if E then if E then other else other` has two parse trees (the `else` can associate with either `if`). Most languages resolve this by convention (else associates with the nearest unmatched if), which corresponds to Parse Tree 2 (else goes with the inner if). This convention is imposed as a disambiguation rule, not by grammar rewriting.

## Parse Trees and Syntax-Directed Translation

Parse trees are not just about membership — they carry semantic information. Compilers use **syntax-directed translation (SDT)** to attach semantic actions to grammar rules. During parsing, when rule A → α is applied, the associated action computes an attribute value (e.g., the type of an expression, the value of a constant, the generated code). The unambiguous grammar is essential here: if a string had two parse trees, the compiler would not know which semantic actions to apply.
