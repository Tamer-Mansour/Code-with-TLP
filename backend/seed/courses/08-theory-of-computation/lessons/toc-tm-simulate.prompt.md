# Simulate a Turing Machine

Given a Turing machine description and an input string, simulate the TM and report whether it accepts, rejects, or appears to loop (runs more than the given step limit without halting).

## Input Format

```
n_states n_tape_symbols
tape_symbols  (space-separated, include _ as blank)
accept_state
reject_state
n_transitions
state symbol new_state new_symbol direction
...  (one transition per line; direction is L or R)
start_state
step_limit
input_string
```

All states are integers (0-indexed). The input string uses only non-blank tape symbols. The input string may be empty (represented as an empty line).

## Output

Print exactly one of:
- `accept`
- `reject`
- `loop`

## Example

A TM with 3 states that accepts any non-empty binary string ending in 1:

```
3 3
0 1 _
1
2
4
0 0 0 0 R
0 1 0 1 R
0 _ 1 _ L
1 1 1 _ R
1
10
101
```

States: 0 (scanning right), 1 (check last was 1), 2 (reject). Accept=1, Reject=2.
- Transitions: from 0, on 0 or 1, stay in 0 and move right. On _, move to state 1 and move left.
- From 1, on 1 (the last symbol) → accept state by moving right... 

Actually the simpler encoding below is used in the test cases. Study the test cases carefully.
