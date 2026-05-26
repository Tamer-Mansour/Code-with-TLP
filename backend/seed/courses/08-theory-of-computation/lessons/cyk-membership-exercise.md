# CYK Membership Testing

In this exercise you will implement the Cocke-Younger-Kasami (CYK) algorithm to test whether a string belongs to a context-free language given as a grammar in Chomsky Normal Form (CNF).

## Background

The CYK algorithm uses dynamic programming on the table T[i][j] = set of variables that derive the substring w[i..j]. It fills the table bottom-up:

- Base: T[i][i] = {A | A → w[i] is a rule}.
- Step: T[i][j] = {A | A → BC ∈ R, ∃k: B ∈ T[i][k] and C ∈ T[k+1][j]}.
- Accept iff S ∈ T[0][n-1].

## Input Format

```
Line 1: V T S                      -- V variables, T terminals, start variable index
Line 2: var_0 var_1 ... var_{V-1}  -- variable names (strings)
Line 3: term_0 ... term_{T-1}      -- terminal symbols (single chars)
Line 4: R                          -- number of rules
Next R lines: each rule in one of two forms:
    A -> B C     (binary rule, A B C are variable names)
    A -> t       (terminal rule, A is variable name, t is terminal char)
Last line: word                    -- input word (non-empty)
```

## Output

Print `accept` or `reject`.

## Example

Grammar for {aⁿbⁿ | n≥1} in CNF:
```
S → AB | SC  (where C is used for S paired with B)
A → a
B → b
C → SB
```

Actually minimal CNF for {aⁿbⁿ|n≥1}: S→AB, S→AC (with C→SB), A→a, B→b is not quite right. See prompt file for a clean example.
