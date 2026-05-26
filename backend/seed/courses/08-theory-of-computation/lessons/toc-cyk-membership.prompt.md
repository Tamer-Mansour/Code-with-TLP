# CYK Membership

Given a context-free grammar in Chomsky Normal Form (CNF), determine whether a given string is in the language using the CYK algorithm.

## Input Format

```
V R                     -- V variables (0..V-1), R rules
var_0 var_1 ...         -- variable names (one line, space-separated)
start_idx               -- index of start variable (0-based)
[R lines]               -- each rule is one of:
                        --   A B C   (binary rule A → BC; A, B, C are variable indices)
                        --   A t     (terminal rule A → t; A is variable index, t is single char)
word                    -- input word (non-empty string)
```

Rules with 3 integers are binary rules; rules with 1 integer and 1 char are terminal rules.

## Output

Print `accept` or `reject`.

## Example

Grammar: S → AB, A → a, B → b (recognizes only "ab").

- V=2, R=3 rules: [S→AB, A→a, B→b]. Variables: S(0), A(1), B(2)... wait, V=3.

Let's be explicit:
- V=3 variables: S(0), A(1), B(2)
- R=3 rules: 0 1 2 (S→AB), 1 a (A→a), 2 b (B→b)
- Start: 0

For word "ab":
- T[0][0]: rules giving terminal 'a' → {A=1}
- T[1][1]: rules giving terminal 'b' → {B=2}
- T[0][1]: k=0: A∈T[0][0]✓, B∈T[1][1]✓, rule S→AB → {S=0}
- S(0) ∈ T[0][1] → **accept** ✓

Input:
```
3 3
S A B
0
0 1 2
1 a
2 b
ab
```

Output: `accept`

## Constraints

- 1 ≤ V ≤ 20
- 1 ≤ R ≤ 100
- 1 ≤ |word| ≤ 30
- Grammar is guaranteed to be in CNF (only binary and terminal rules)
- Terminals are lowercase letters
