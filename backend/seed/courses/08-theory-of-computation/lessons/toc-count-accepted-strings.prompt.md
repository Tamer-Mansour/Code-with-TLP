# Count Accepted Strings of Length N

Given a DFA and an integer N, count the number of distinct strings of exactly length N that the DFA accepts.

This problem connects automata theory to combinatorics: you are computing the **growth function** of the DFA's language restricted to strings of a fixed length.

## Input Format

```
n a
sym1 sym2 ... syma
t(0,sym1) t(0,sym2) ... t(0,syma)
t(1,sym1) ...
...
t(n-1,sym1) ...
start
acc1 acc2 ...
N
```

- Line 1: integers `n` (number of states, 0-indexed) and `a` (alphabet size).
- Line 2: the `a` alphabet symbols (single characters, space-separated).
- Lines 3 to n+2: transition table (same format as the DFA-simulate exercise).
- Line n+3: start state.
- Line n+4: accept states (space-separated).
- Line n+5: integer N (0 ≤ N ≤ 30).

## Output

Print a single integer: the number of strings of length exactly N accepted by the DFA.

## Example

DFA with 2 states accepting binary strings with an even number of 1s (same as in the DFA simulation lesson):

```
2 2
0 1
0 1
1 0
0
0
3
```

Strings of length 3 over {0,1}: 000, 001, 010, 011, 100, 101, 110, 111.
Even number of 1s: 000 (0 ones), 011 (2 ones), 101 (2 ones), 110 (2 ones) → 4 strings.

Expected output: `4`
