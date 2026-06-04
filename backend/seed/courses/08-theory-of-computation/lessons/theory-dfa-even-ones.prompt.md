# DFA Simulator: Even Number of 1s

Simulate a DFA that accepts binary strings containing an **even number of 1s**.

The DFA has two states:
- `q0` — start state and accept state (even number of 1s seen, including zero)
- `q1` — non-accepting state (odd number of 1s seen)

**Transitions:**
- On `0`: state does not change (reading a 0 does not affect parity)
- On `1`: state toggles between q0 and q1

## Input Format

- Line 1: an integer `T` (1 ≤ T ≤ 100) — the number of test strings
- Next `T` lines: each line is a binary string consisting only of characters `0` and `1`. The empty string is represented by the word `epsilon`.

## Output Format

For each test string (in order), print `ACCEPT` if the DFA accepts it, or `REJECT` otherwise.

## Examples

**Input:**
```
4
0100
111
1010
epsilon
```

**Output:**
```
ACCEPT
REJECT
ACCEPT
ACCEPT
```

**Explanation:**
- `"0100"` has one 1 (odd) — REJECT
- `"111"` has three 1s (odd) — REJECT
- `"1010"` has two 1s (even) — ACCEPT
- `epsilon` (empty string) has zero 1s (even) — ACCEPT

## Constraints

- 1 ≤ T ≤ 100
- Each binary string has length at most 1000 characters (or is `epsilon`)
- Characters are only `0` and `1` (plus the literal word `epsilon` for the empty string)
