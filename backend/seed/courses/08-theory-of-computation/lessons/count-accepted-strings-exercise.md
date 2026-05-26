# Count Accepted Strings of Length N

This exercise connects automata theory to dynamic programming. Given a DFA and an integer N, you must count how many distinct strings of exactly length N the DFA accepts.

## Key Insight

Rather than enumerating all aᴺ strings (exponential), use the DFA's structure:

- Let `dp[s]` = number of strings of the current length that leave the DFA in state `s`.
- Start: `dp[start] = 1`, all others 0.
- Each step (for each of N symbols): for every state `s` and alphabet symbol `a`, add `dp[s]` paths to `dp[δ(s, a)]`.
- Answer: sum of `dp[s]` for all `s` in the accept set.

This is O(N × |Q| × |Σ|) — polynomial even when N = 30 and the alphabet has many symbols.

## Connection to Theory

The **growth function** γ_L(n) = |{w ∈ L \| |w| = n}| is an important language invariant:

- Regular languages have **ultimately periodic** growth functions (by the theory of linear recurrences over transition matrices).
- For a DFA with n states, the sequence γ_L(0), γ_L(1), γ_L(2), … satisfies a linear recurrence of order ≤ n.
- Context-free languages can have polynomial or exponential growth functions.

The DP you implement is computing a column of the **transfer matrix** Tⁿ where T[i][j] = number of alphabet symbols taking state i to state j.

## Exercise

See the prompt below for the exact input/output format and test cases.
