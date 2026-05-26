# Simulating a DFA

Running a DFA by hand on paper is straightforward, but implementing the simulation in code solidifies the formal model. This lesson walks through how to represent and execute a DFA programmatically.

## DFA as a Data Structure

A DFA M = (Q, Σ, δ, q₀, F) maps naturally to:

```python
# States: integers 0..n-1 (or strings)
# Alphabet: a set of characters
# Transition table: dict[(state, symbol)] -> state
# Start state: integer
# Accept states: set of integers
```

## Reading the Encoding

For the graded exercise in this module, the DFA is provided on standard input in the following format:

```
Line 1: n a   -- n states (0..n-1), a alphabet symbols
Line 2: symbols  -- the alphabet (space-separated single characters)
Line 3..n+2: one line per state, listing δ(state, sym) for each sym in order
Line n+3: start_state
Line n+4: accept_states (space-separated)
Line n+5: input_string  -- the string to test
```

## Simulation Loop

```python
import sys

def simulate_dfa(n, alphabet, transitions, start, accept, word):
    state = start
    for ch in word:
        if ch not in alphabet:
            return "reject"
        state = transitions[state][ch]
    return "accept" if state in accept else "reject"
```

The loop is O(|w|) time — reading each symbol once.

## Trace Example

Consider the DFA that accepts binary strings with an even number of 1s:

| State | 0 | 1 |
|-------|---|---|
| q₀ (even 1s) | q₀ | q₁ |
| q₁ (odd 1s)  | q₁ | q₀ |

Input: "1 0 1 1"

- Start q₀
- 1 → q₁  (one 1 seen)
- 0 → q₁  (zeros don't change parity)
- 1 → q₀  (two 1s)
- 1 → q₁  (three 1s)
- Final state q₁ ∉ F → **reject**

Input: "1 0 1":
- q₀ →¹ q₁ →⁰ q₁ →¹ q₀ ∈ F → **accept**

## Why Simulation Matters

- Compilers use DFAs (as finite-state machines) to implement lexers — recognizing keywords, identifiers, and literals character-by-character in O(n) time.
- Network packet classifiers use DFA-like structures for pattern matching at line speed.
- Text search tools (grep, awk) compile regular expressions into DFAs.

Understanding the simulation loop is the bridge between the mathematical definition and real-world applications. The exercise attached to this lesson asks you to implement exactly this simulation.
