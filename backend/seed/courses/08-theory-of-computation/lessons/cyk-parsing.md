# CYK Parsing: The Cocke-Younger-Kasami Algorithm

The **CYK algorithm** (independently discovered by Cocke, Younger, and Kasami in the 1960s) decides in O(n³·|G|) time whether a string w belongs to a context-free language L(G), where G is in Chomsky Normal Form. It is a beautiful example of dynamic programming applied to formal language theory.

## Prerequisites: CNF

The CYK algorithm requires the grammar to be in **Chomsky Normal Form (CNF)**: every rule is either A → BC or A → a (plus S → ε if ε ∈ L(G)).

Every CFG can be converted to CNF (see the Context-Free Grammars lesson). The conversion may increase the grammar size polynomially but not more.

## The Core Idea

For string w = w₁w₂…wₙ, define:

> **T[i][j]** = the set of variables A such that A ⇒* wᵢwᵢ₊₁…wⱼ

(the set of variables that can derive the substring from position i to j, inclusive).

**w ∈ L(G) iff S ∈ T[1][n].**

## Base Case (single characters)

For each position i (1 ≤ i ≤ n):

> T[i][i] = {A ∈ V \| A → wᵢ is a rule in G}

This captures which variables derive the single symbol at position i.

## Recursive Case (substrings of length ≥ 2)

For each length ℓ = 2, 3, …, n and each starting position i (1 ≤ i ≤ n-ℓ+1), let j = i+ℓ-1:

> T[i][j] = {A \| ∃ rule A → BC and ∃ split point k (i ≤ k < j): B ∈ T[i][k] and C ∈ T[k+1][j]}

For each A → BC rule, try all split points k. A variable A goes into T[i][j] if the left part derives w[i..k] (B in T[i][k]) and the right part derives w[k+1..j] (C in T[k+1][j]).

## Algorithm (Pseudocode)

```python
def cyk(grammar_rules, start, w):
    n = len(w)
    # T[i][j] is a set of variable names
    T = [[set() for _ in range(n)] for _ in range(n)]

    # Base case: single characters
    for i in range(n):
        for A, rhs in grammar_rules:
            if rhs == [w[i]]:  # A → wᵢ
                T[i][i].add(A)

    # Fill by increasing substring length
    for length in range(2, n+1):         # substring length
        for i in range(n - length + 1):  # start index
            j = i + length - 1           # end index
            for k in range(i, j):        # split point
                for A, (B, C) in binary_rules:  # A → BC
                    if B in T[i][k] and C in T[k+1][j]:
                        T[i][j].add(A)

    return start in T[0][n-1]
```

## Worked Example

**Grammar G** (already in CNF):
```
S → AB | BC
A → BA | a
B → CC | b
C → AB | a
```

**String w = "baaba"** (n = 5, positions 1..5 using 1-indexing).

### Step 1: Base cases (length 1)

| Position | Symbol | Variables deriving it |
|----------|--------|-----------------------|
| T[1][1] | b | {B} |
| T[2][2] | a | {A, C} |
| T[3][3] | a | {A, C} |
| T[4][4] | b | {B} |
| T[5][5] | a | {A, C} |

### Step 2: Length 2 substrings

**T[1][2]** = "ba": split at k=1: B∈T[1][1], {A,C}∈T[2][2]
- S → AB? A∈T[1][1]? No. S → BC? B∈T[1][1]✓, C∈T[2][2]✓ → S ∈ T[1][2]
- A → BA? B∈T[1][1]✓, A∈T[2][2]✓ → A ∈ T[1][2]
- B → CC? C∈T[1][1]? No.
- C → AB? A∈T[1][1]? No.
→ **T[1][2] = {S, A}**

**T[2][3]** = "aa": split at k=2: {A,C}∈T[2][2], {A,C}∈T[3][3]
- S → AB? A∈T[2][2]✓, B∈T[3][3]? No.
- S → BC? B∈T[2][2]? No.
- A → BA? B∈T[2][2]? No.
- B → CC? C∈T[2][2]✓, C∈T[3][3]✓ → B ∈ T[2][3]
- C → AB? A∈T[2][2]✓, B∈T[3][3]? No.
→ **T[2][3] = {B}**

**T[3][4]** = "ab": split at k=3: {A,C}∈T[3][3], B∈T[4][4]
- S → AB? A∈T[3][3]✓, B∈T[4][4]✓ → S ∈ T[3][4]
- A → BA? No. B → CC? No.
- C → AB? A∈T[3][3]✓, B∈T[4][4]✓ → C ∈ T[3][4]
→ **T[3][4] = {S, C}**

**T[4][5]** = "ba": (same structure as T[1][2])
- S → BC: B∈T[4][4]✓, C∈T[5][5]✓ → S
- A → BA: B∈T[4][4]✓, A∈T[5][5]✓ → A
→ **T[4][5] = {S, A}**

### Step 3: Length 3 substrings

**T[1][3]** = "baa": splits at k=1 and k=2.
- k=1: T[1][1]={B}, T[2][3]={B}. Rules A→BC need B∈left, C∈right? No. S→BC: B✓,B? no C. B→CC: no C in left.
- k=2: T[1][2]={S,A}, T[3][3]={A,C}. S→AB: A∈{S,A}✓, B∈{A,C}? No. S→BC: B∈{S,A}? No. A→BA: B∈{S,A}? No. C→AB: A∈{S,A}✓, B∈{A,C}? No.
→ **T[1][3] = {}**

**T[2][4]** = "aab": splits at k=2 and k=3.
- k=2: T[2][2]={A,C}, T[3][4]={S,C}. A→BA: B? No. S→BC: B∈{A,C}? No. S→AB: A∈{A,C}✓, B∈{S,C}? No. C→AB: same. B→CC: C∈{A,C}✓, C∈{S,C}✓ → B.
- k=3: T[2][3]={B}, T[4][4]={B}. S→AB: A∈{B}? No. A→BA: B✓, A∈{B}? No. B→CC: C? No.
→ **T[2][4] = {B}**

**T[3][5]** = "aba": splits at k=3 and k=4.
- k=3: T[3][3]={A,C}, T[4][5]={S,A}. S→AB: A✓, B∈{S,A}? No. S→BC: B? No. A→BA: B? No. C→AB: A✓, B∈{S,A}? No.
- k=4: T[3][4]={S,C}, T[5][5]={A,C}. S→AB: A∈{S,C}? No. S→BC: B∈{S,C}? No. A→BA: B? No. B→CC: C∈{S,C}✓, C∈{A,C}✓ → B.
→ **T[3][5] = {B}**

### Step 4: Length 4 substrings

**T[1][4]** = "baab": splits at k=1,2,3.
- k=1: T[1][1]={B}, T[2][4]={B}. S→BC: B✓, C∈{B}? No. B→CC: no C.
- k=2: T[1][2]={S,A}, T[3][4]={S,C}. S→AB: A∈{S,A}✓, B∈{S,C}? No. S→BC: B∈{S,A}? No. A→BA: B? No. C→AB: A✓, B? No.
- k=3: T[1][3]={}, so nothing.
→ **T[1][4] = {}**

**T[2][5]** = "aaba": splits at k=2,3,4.
- k=2: T[2][2]={A,C}, T[3][5]={B}. S→AB: A✓, B✓ → **S ∈ T[2][5]**. C→AB: A✓, B✓ → C.
- k=3: T[2][3]={B}, T[4][5]={S,A}. A→BA: B✓, A✓ → A.
- k=4: T[2][4]={B}, T[5][5]={A,C}. S→BC: B✓, C✓ → S (already). A→BA: B✓,A✓→ A (already).
→ **T[2][5] = {S, A, C}**

### Step 5: Full string T[1][5] = "baaba"

Splits at k=1,2,3,4.
- k=1: T[1][1]={B}, T[2][5]={S,A,C}. S→BC: B✓, C✓ → **S ∈ T[1][5]**. ✓

**S ∈ T[1][5] → "baaba" ∈ L(G).** Accept!

## Time and Space Complexity

- **Cells:** O(n²) entries in the triangular table.
- **Each cell:** Try all rules A → BC (|R| rules) and all split points k (up to n). Each check is O(1) using set membership. Cost per cell: O(n·|R|).
- **Total time:** O(n²) cells × O(n·|R|) per cell = **O(n³·|R|)**.
- **Space:** O(n²·|V|) to store the table.

For most practical grammars, |R| and |V| are small constants, so CYK is effectively O(n³).

## CYK and Ambiguity

CYK as described only answers membership (is w ∈ L(G)?). With a minor modification — storing not just which variables go in T[i][j] but also *which rule and split point* caused each entry — CYK becomes a **chart parser** that can extract a parse tree or count all parse trees. The number of parse trees is proportional to the number of ambiguous derivations and can be exponential in the worst case.

## Practical Significance

CYK is used in:
- **NLP parsers** (natural language processing): parsing sentences with probabilistic CFGs (PCFGs) for statistical parsing.
- **Compiler verification:** Checking that a token stream matches a grammar.
- **Biological sequence analysis:** RNA secondary structure prediction uses an analogous DP on a grammar-like formalism.
