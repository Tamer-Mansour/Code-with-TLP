# NFA Simulator

Simulate a nondeterministic finite automaton (NFA with ε-transitions) on a given input word. Print `accept` if the NFA accepts, otherwise `reject`.

## Input Format

```
n a              -- n states (0..n-1), a alphabet symbols
sym1 sym2 ...    -- alphabet symbols (single chars, space-separated)
[n*(a+1) lines]  -- for each state i (0..n-1), for each of (a+1) symbols (alphabet + "e" for ε):
                 --   a line with space-separated destination states, or "-" if no transitions
start            -- start state
k                -- number of accept states
acc1 acc2 ...    -- accept states (space-separated)
word             -- input word (may be empty line)
```

The transition block has exactly n*(a+1) lines. For state i, the first a lines correspond to the a alphabet symbols (in the order given on line 2), and the (a+1)-th line gives ε-transitions. "-" means no transitions from that state on that symbol.

## Example

NFA for strings over {a,b} that contain "ab" as a substring:
- 3 states, alphabet {a,b}
- δ(0,a)={0,1}, δ(0,b)={0}, δ(0,ε)=∅
- δ(1,a)=∅, δ(1,b)={2}, δ(1,ε)=∅
- δ(2,a)={2}, δ(2,b)={2}, δ(2,ε)=∅
- Start: 0, Accept: {2}

```
3 2
a b
0 1
0
-
-
2
-
2 2
2 2
0
1
2
bab
```

The NFA on "bab": start {0} →b {0} →a {0,1} →b {0,2} → intersects {2} → **accept**.

## Constraints

- 1 ≤ n ≤ 15
- 1 ≤ a ≤ 4
- 0 ≤ |word| ≤ 50
- All characters in word are from the alphabet
