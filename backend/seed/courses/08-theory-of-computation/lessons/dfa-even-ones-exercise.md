# DFA Simulator: Even Number of 1s

This exercise puts theory directly into code. You will implement a simulation of the classic two-state DFA that accepts binary strings containing an even number of 1s. It is one of the canonical examples used in every automata theory textbook — simple enough to trace by hand, yet rich enough to demonstrate every element of the formal DFA definition.

## The DFA

Alphabet: {0, 1}

**States:**
- `q0` — start state and **accept** state: an even number of 1s have been read so far (including zero 1s).
- `q1` — reject state: an odd number of 1s have been read.

**Transition table:**

| State | 0 | 1 |
|-------|---|---|
| q0 | q0 | q1 |
| q1 | q1 | q0 |

Reading a `0` never changes parity — the state stays the same. Reading a `1` flips parity — the state toggles.

**Formal definition:**  
M = ({q0, q1}, {0, 1}, δ, q0, {q0})

where δ is given by the table above.

## Why This Works

The DFA tracks exactly one bit of information: the parity of the number of 1s seen. This is sufficient because "even number of 1s" depends only on this parity, which can be maintained with just two states.

This DFA is **minimal** (the Myhill-Nerode theorem confirms it: the empty string ε and the string "1" are distinguishable — "1" appended to ε gives "1" which is rejected from q0, but "1" appended to "1" gives "11" which is accepted from q1 — so two equivalence classes, two states).

## Tracing Examples

**Input: "0100"**  
q0 →⁰ q0 →¹ q1 →⁰ q1 →⁰ q1  
Final state q1 — **REJECT** (one 1 seen, odd)

Wait — re-check: "0100" has exactly one 1.  
q0 →⁰ q0 →¹ q1 →⁰ q1 →⁰ q1 → final q1 → REJECT.

**Input: "1010"**  
q0 →¹ q1 →⁰ q1 →¹ q0 →⁰ q0  
Final state q0 — **ACCEPT** (two 1s seen, even)

**Input: "epsilon" (empty string)**  
Start in q0, no symbols — final state q0 — **ACCEPT** (zero 1s, and 0 is even)

## Connection to Regular Languages

This DFA witnesses that the language L = {w ∈ {0,1}* | w has an even number of 1s} is **regular**. The corresponding regular expression is:

```
(0*(10*10*)*)
```

Or equivalently: `0*(10*10*)*0*` — zero or more 0s, followed by pairs of 1s with 0s interspersed.

## Further Reading

- Sipser §1.1 (DFA definition, examples, formal language definition) — MIT OpenCourseWare: https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/
- Maheshwari & Smid, Chapter 1 (formal automata definition and simulation) — https://cglab.ca/~michiel/TheoryOfComputation/TheoryOfComputation.pdf
