# Context-Free Grammars

A **context-free grammar (CFG)** is a recursive rule system for generating strings. CFGs describe a strictly larger class of languages than regular expressions (for example, {aⁿbⁿ \| n ≥ 0} is context-free but not regular) and are the foundation of programming language syntax specification.

## Formal Definition

A CFG is a 4-tuple G = (V, Σ, R, S) where:

| Component | Type | Meaning |
|-----------|------|---------|
| V | finite set | **Variables** (non-terminals), conventionally uppercase: S, A, B, … |
| Σ | finite set | **Terminals** (disjoint from V): the actual output symbols |
| R | finite set | **Rules** (productions): each rule has the form A → w where A ∈ V and w ∈ (V ∪ Σ)\* |
| S | element of V | **Start variable** |

Variables represent syntactic categories; terminals are the actual symbols in the generated strings.

## Derivations

A **single derivation step** u ⇒ v replaces one variable A in u with the right-hand side of some rule A → w. Formally: if u = αAβ and A → w ∈ R, then u ⇒ αwβ.

A **derivation** is a sequence u₀ ⇒ u₁ ⇒ … ⇒ uₙ. Write u ⇒* v if v is reachable from u in zero or more steps.

The **language** of G: L(G) = {w ∈ Σ\* \| S ⇒* w}.

A **sentential form** is any string in (V ∪ Σ)\* reachable from S. A **sentence** is a sentential form with no variables (a string in Σ\*).

**Leftmost derivation**: always expand the leftmost variable. Every string in L(G) has a leftmost derivation, and parse trees correspond bijectively to leftmost derivations.

## Worked Example 1: {aⁿbⁿ | n ≥ 0}

Grammar G₁:
```
S → aSb | ε
```

**Derivation of "aaabbb"** (leftmost):
```
S ⇒ aSb ⇒ aaSbb ⇒ aaaSbbb ⇒ aaaεbbb = aaabbb
```

This grammar generates exactly {aⁿbⁿ \| n ≥ 0}. The recursive rule S → aSb "nests" each a–b pair inside the previous one, allowing the grammar to match arbitrarily many a's with the corresponding b's. No DFA can do this (it would need to count n, which is unbounded).

## Worked Example 2: Balanced Parentheses

Grammar G₂:
```
S → (S) | SS | ε
```

Generates all balanced parenthesis strings. For example:
```
S ⇒ SS ⇒ (S)S ⇒ (ε)S = ()S ⇒ ()(S) ⇒ ()(SS) ⇒ ()(()S) ⇒ ()((ε)S) = ()(()S) ⇒ ()(()ε) = ()(())
```
Result: "()(())" — a valid balanced string. ✓

## Worked Example 3: Arithmetic Expressions with Precedence

Grammar G₃:
```
E → E + T | T
T → T * F | F
F → (E) | id | num
```

Derivation of "id + id * id":
```
E ⇒ E + T ⇒ T + T ⇒ F + T ⇒ id + T ⇒ id + T * F ⇒ id + F * F ⇒ id + id * F ⇒ id + id * id
```

The grammar encodes operator precedence: \* binds tighter than + because T (the multiplicative level) appears in E's rules as a unit. This grammar is unambiguous and generates correct parse trees for all arithmetic expressions.

## Parse Trees

A **parse tree** (derivation tree) is a tree that records a derivation:
- The root is labeled S.
- Each interior node is labeled with a variable A.
- The children of a node labeled A correspond to the symbols in the right-hand side of the rule A → w applied at that step.
- Leaves are terminals or ε.
- The **yield** (left-to-right concatenation of leaves) is the generated string.

**Parse tree for "aabb" using G₁:**
```
        S
      / | \
     a  S  b
       / | \
      a  S  b
         |
         ε
```
Yield: a · a · ε · b · b = "aabb" ✓

Every parse tree corresponds to exactly one leftmost derivation. If a string has two different parse trees, the grammar is **ambiguous**.

## Chomsky Normal Form (CNF)

Every CFG G with ε ∉ L(G) can be converted to an equivalent CFG in **Chomsky Normal Form (CNF)** where every rule has the form:
- A → BC (exactly two variables), or
- A → a (exactly one terminal)

If ε ∈ L(G), we additionally allow S → ε for the start variable only (and S does not appear on any rule's right-hand side).

### CNF Conversion Algorithm

Given G = (V, Σ, R, S):

**Step 1 — Add new start:** Add S₀ → S. (Prevents S from appearing in rule right-hand sides.)

**Step 2 — Eliminate ε-productions:** Find all **nullable** variables (those deriving ε). For each rule containing a nullable variable A, add a copy of the rule with A removed. Remove ε-rules (except S₀ → ε if ε ∈ L).

**Step 3 — Eliminate unit rules:** A unit rule has the form A → B (single variable on RHS). Replace A → B combined with B → w by A → w for all rules B → w. Repeat until no unit rules remain.

**Step 4 — Convert long rules:** Replace A → X₁X₂…Xₖ (k ≥ 3) with A → X₁A₁, A₁ → X₂A₂, …, A_{k-2} → X_{k-1}Xₖ. (Introduce fresh variables.)

**Step 5 — Isolate terminals:** In rules A → BC, if B or C is a terminal a, replace it with a fresh variable Tₐ and add Tₐ → a.

### CNF Example

Convert G: S → AB, A → aA | a, B → bB | b to CNF.

Step 1: Add S₀ → S. (No ε-rules, no unit rules to eliminate beyond A → a and B → b which are already A → a.)

Actually A → a and B → b are already CNF rules. A → aA: introduce Tₐ → a, then A → TₐA. Similarly B → bB becomes B → TbB with Tb → b.

Final CNF:
```
S₀ → S
S  → AB
A  → TₐA | a
B  → TbB | b
Tₐ → a
Tb → b
```

CNF is used in the CYK algorithm and in the pumping lemma proof for CFLs.

## The CYK Algorithm (Preview)

The **Cocke-Younger-Kasami (CYK) algorithm** decides in O(n³·|G|) time whether w ∈ L(G) for a CFG G in CNF. It uses dynamic programming: the table entry T[i][j] = set of variables that derive the substring w[i..j]. CYK is covered in depth in the next module.

## Context-Free Languages: Larger Than Regular

The regular languages are strictly contained in the context-free languages (CFLs). CFGs add the power of **matching nested structures** via recursive rules and a stack (as we'll see via PDAs). Examples of CFLs that are not regular:

- {aⁿbⁿ \| n ≥ 0}
- {wwᴿ \| w ∈ {a,b}\*} (even-length palindromes)
- {w \| w ∈ {(,)}\* and the parentheses are balanced}
- All context-free programming language constructs (nested blocks, matched brackets, arithmetic expressions)

The boundary of what CFGs can express is explored in the next module via the PDA model and the CFL pumping lemma.
