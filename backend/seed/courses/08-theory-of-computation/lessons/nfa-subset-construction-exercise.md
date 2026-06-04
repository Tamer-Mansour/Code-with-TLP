# NFA to DFA: Subset Construction in Practice

The subset construction is the algorithm that converts any NFA into an equivalent DFA by treating each reachable **set of NFA states** as a single DFA state. This exercise makes you implement that algorithm and count how many DFA states result — a direct measure of the potential exponential blowup.

## Review: The Algorithm

Given NFA N = (Q, Σ, δ_N, q₀, F_N), the equivalent DFA M is built as follows:

1. **Start state of DFA:** S₀ = ε-closure({q₀})
2. **For each DFA state S (a subset of Q) and each a ∈ Σ:**  
   δ_M(S, a) = ε-closure(∪_{q ∈ S} δ_N(q, a))
3. **Accept states of DFA:** all S such that S ∩ F_N ≠ ∅
4. **Only reachable subsets** are included (BFS/DFS from S₀)

The total number of DFA states is the number of distinct reachable subsets of Q discovered during this process.

## Why Reachable States Only?

The full powerset 𝒫(Q) has 2^|Q| subsets. For a 10-state NFA that could be 1024 DFA states. In practice, most subsets are unreachable from the start subset. The reachable-subsets-only construction gives an equivalent DFA that may be dramatically smaller.

**Key insight:** The subset construction proves NFA ≡ DFA in expressiveness. Every language recognizable by an NFA is also recognizable by a DFA (same language, possibly more states).

## Example

NFA over {a, b} with 3 states:
```
State 0 (start): on a → {0,1}; on b → {0}
State 1:         on a → {2};   on b → ∅
State 2 (accept):on a → ∅;    on b → ∅
```

Subset construction (no ε-transitions here):

| DFA State (subset) | On a | On b | Accept? |
|--------------------|------|------|---------|
| {0} (start) | {0,1} | {0} | No |
| {0,1} | {0,1,2} | {0} | No |
| {0,1,2} | {0,1,2} | {0} | **Yes** (contains 2) |

Total DFA states: **3** (only {0}, {0,1}, {0,1,2} are reachable — not the empty set or {1}, {2}, etc.)

## Correctness Note

A common misconception: "NFA is more powerful than DFA." This is false. The subset construction is exactly the proof that they are **equally powerful**. An NFA can be exponentially more compact (fewer states) but it cannot recognize any language that a DFA cannot. The converse is also true — every DFA is trivially an NFA (with |δ(q,a)| ≤ 1).

## Complexity

- Reachable-subset construction: O(2^n · |Σ|) time and space in the worst case, where n = |Q|.
- Many practical NFAs (e.g., compiled from simple regex) produce DFAs with ≤ n · |Σ| states.

## Further Reading

- Sipser §1.2–1.3 — MIT OCW lecture notes: https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/
- Critchlow & Eck, Chapter 3 (regular expressions, FSAs, subset construction) — https://math.hws.edu/FoundationsOfComputation/FoundationsOfComputation_2.3.2_6x9.pdf
