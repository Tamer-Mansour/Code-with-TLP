# Bounded Turing Machine Simulator

Simulate a Turing Machine (TM) on the **empty string** (tape initialized to all blanks) and determine whether it halts within K steps, and if so, whether it accepts or rejects.

## Tape Conventions

- The tape is infinite in both directions and initially filled with the blank symbol `B`.
- The head starts at position 0.
- If the TM is in a state with no defined transition for the current symbol, it **rejects immediately**.
- The special state `qaccept` halts and accepts; `qreject` halts and rejects.

## Input Format

- Line 1: two integers `R` and `K` — the number of transition rules and the step limit.
- Next `R` lines: each line has 5 space-separated fields:
  `current_state  read_symbol  next_state  write_symbol  direction`
  - `direction` is `L` (move head left) or `R` (move head right).
  - Symbols are single tokens: `0`, `1`, or `B` (blank).
  - States are strings like `q0`, `q1`, `qaccept`, `qreject`.

The start state is always `q0`. The accept state is always `qaccept`. The reject state is always `qreject`.

## Output Format

One of three outputs:
- `HALT_ACCEPT` — the TM reached `qaccept` within K steps.
- `HALT_REJECT` — the TM reached `qreject` (or had no transition) within K steps.
- `DID_NOT_HALT` — the TM did not halt within K steps.

## Examples

**Example 1:**
```
Input:
2 100
q0 B qaccept B R
q0 0 qreject 0 R

Output:
HALT_ACCEPT
```

*The TM starts in q0, reads blank B, transitions to qaccept. Halts and accepts on step 1.*

**Example 2:**
```
Input:
1 10
q0 B q0 B R

Output:
DID_NOT_HALT
```

*The TM loops forever moving right over blanks, never reaching qaccept or qreject within 10 steps.*

**Example 3:**
```
Input:
2 50
q0 B q1 1 R
q1 B qreject B L

Output:
HALT_REJECT
```

*The TM writes 1, moves right, reads blank, transitions to qreject.*

## Constraints

- 1 ≤ R ≤ 50
- 1 ≤ K ≤ 10000
- States are non-empty strings of at most 20 characters (alphanumeric)
- Tape symbols are exactly `0`, `1`, or `B`
- No two transitions have the same (current_state, read_symbol) pair
