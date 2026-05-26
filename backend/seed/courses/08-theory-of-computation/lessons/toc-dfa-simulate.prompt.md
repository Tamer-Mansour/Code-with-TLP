# Simulate a DFA

Given a DFA description and an input string, determine whether the DFA accepts or rejects the string.

## Input Format

```
n a
sym1 sym2 ... syma
t(0,sym1) t(0,sym2) ... t(0,syma)
t(1,sym1) t(1,sym2) ... t(1,syma)
...
t(n-1,sym1) t(n-1,sym2) ... t(n-1,syma)
start
acc1 acc2 ...
input_string
```

- Line 1: two integers `n` (number of states, labeled 0 to n-1) and `a` (alphabet size).
- Line 2: the `a` alphabet symbols separated by spaces (single characters).
- Lines 3 to n+2: the transition table. Line `i+3` (0-indexed) gives the transitions from state `i` for each alphabet symbol in order.
- Line n+3: the start state (integer 0..n-1).
- Line n+4: the accept states as space-separated integers (at least one).
- Line n+5: the input string (may be empty — represented as an empty line).

## Output

Print `accept` or `reject` on a single line.

## Example

Input:
```
2 2
0 1
0 1
1 0
0
0
101
```

This encodes the DFA with states {0,1}, alphabet {0,1}, transitions δ(0,0)=0, δ(0,1)=1, δ(1,0)=1, δ(1,1)=0. Start=0, Accept={0}. It accepts binary strings with an even number of 1s.

For input "101": 0 →¹ 1 →⁰ 1 →¹ 0. Final state 0 is in Accept → **accept**.
