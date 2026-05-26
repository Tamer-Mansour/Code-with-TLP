# Simulating an NFA

In this exercise you will implement an NFA simulator that correctly handles ε-transitions by computing ε-closure at every step.

## What You Need to Know

An NFA processes input by maintaining the set of currently "active" states. The ε-closure of a set S is the set of all states reachable from S by zero or more ε-transitions alone (without consuming input). The simulation:

1. Start with S = ε-closure({start}).
2. For each input character c: S ← ε-closure(∪_{q∈S} δ(q,c)).
3. Accept iff S ∩ F ≠ ∅.

ε-closure is computed by a BFS/DFS following ε-labeled edges.

## Input Format

```
n a               -- n states (0..n-1), a alphabet symbols
sym1 sym2 ...     -- alphabet symbols (single chars, space-separated)
[n*(a+1) lines]   -- transitions: for state i (0..n-1),
                  --   line i*(a+1)+0: destinations on symbol 0 (space-sep ints, or "-")
                  --   line i*(a+1)+1: destinations on symbol 1
                  --   ...
                  --   line i*(a+1)+a: ε-destinations (last line per state)
start             -- start state integer
k                 -- number of accept states
acc1 acc2 ...     -- accept states space-separated
word              -- input word (may be empty)
```

## Output

Print `accept` or `reject`.
