# NFA Subset Construction: Count DFA States

Given an NFA (without epsilon-transitions), compute the number of DFA states produced by the **subset construction** using only **reachable subsets**.

The subset construction converts an NFA into an equivalent DFA by making each reachable set of NFA states a single DFA state. Your task is to count how many such reachable subsets exist (including the start subset).

## Input Format

- Line 1: two integers `N` and `A` — the number of NFA states (0-indexed: 0 to N-1) and the alphabet size.
- Line 2: the start state index (a single integer).
- Line 3: space-separated indices of the NFA accept states.
- Next `N * A` lines: the NFA transitions in **state-major order**: for state 0 all A symbols, then state 1 all A symbols, etc.
  - Each line covers one (state, symbol) pair.
  - Each line lists the (space-separated) successor states on that symbol, or the word `empty` if there are none.
  - Format of each line: `<symbol>: <successors...>` (e.g., `a: 0 1` or `b: empty`)

## Output Format

A single integer: the number of DFA states in the equivalent DFA (counting only reachable subsets, including the start subset).

## Notes

- The start subset is {start_state}.
- The empty subset IS a valid DFA state if it is reachable (it is the "dead state"). Count it if reachable.
- No epsilon-transitions in this problem.

## Examples

**Input:**
```
3 2
0
2
a: 0 1
b: 0
a: 2
b: empty
a: empty
b: empty
```

**Output:**
```
3
```

**Explanation:**

The NFA has 3 states (0, 1, 2), alphabet {a, b}, start state 0, accept state {2}.

Transitions (state-major: state 0 a, state 0 b, state 1 a, state 1 b, state 2 a, state 2 b):
- State 0: on a → {0,1}, on b → {0}
- State 1: on a → {2}, on b → ∅
- State 2: on a → ∅, on b → ∅

Subset construction (reachable subsets from {0}):

| Subset | On a | On b |
|--------|------|------|
| {0} | {0,1} | {0} |
| {0,1} | {0,1,2} | {0} |
| {0,1,2} | {0,1,2} | {0} |

Only 3 subsets are reachable → output `3`.

## Constraints

- 1 ≤ N ≤ 8
- 1 ≤ A ≤ 4 (alphabet symbols are 'a', 'b', 'c', 'd' in order)
- 0 ≤ number of accept states ≤ N
