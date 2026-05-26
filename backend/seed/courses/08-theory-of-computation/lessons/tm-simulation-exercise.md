# Simulating a Simple Turing Machine

In this exercise you will simulate a restricted single-tape Turing machine whose behavior is fully specified by a transition table given on standard input. The goal is to trace the TM's computation and report whether it reaches its accept state, reject state, or exceeds the step limit (loop).

## The Turing Machine Model

- **Tape:** A sequence of cells indexed from 0. Initially contains the input string at positions 0..|w|-1; all remaining cells hold the blank symbol `_`.
- **Head:** Starts at position 0. Can move Left (L) or Right (R) on each step. Moving left from position 0 keeps the head at 0.
- **State:** Starts at the given start state.
- **Transitions:** δ(state, symbol) = (new_state, new_symbol, direction). If no transition is defined for (state, symbol), the machine rejects.
- **Halt conditions:** The machine halts immediately upon entering the accept state or the reject state.
- **Step limit:** If the machine has not halted after the given number of steps, report `loop`.

## Input Format

```
n_states n_tape_syms
sym1 sym2 ... sym_n_tape_syms    -- tape symbols (include _ for blank)
accept_state                      -- integer state index
reject_state                      -- integer state index
n_transitions                     -- number of transitions
[n_transitions lines]             -- each: state symbol new_state new_symbol direction (L or R)
start_state
step_limit
input_string                      -- may be empty line
```

## Output

Print exactly one of: `accept`, `reject`, or `loop`.

## What the Exercise Tests

This exercise builds on the DFA simulator in two important ways:
1. The tape is **read-write** — the TM can modify the tape as it runs.
2. The head can move **both directions**, allowing the machine to re-examine symbols.
3. The tape is **unbounded** — the machine reads blank symbols beyond the input.

These three features together give the TM its full computational power. The simulation loop is the heart of any universal Turing machine interpreter.

## Worked Trace

TM that accepts all-zero strings over {0,1} (transitions given):
- `(0, '0') → (0, '0', R)`: scan right over 0s
- `(0, '_') → (1, '_', R)`: reached end of input → accept
- `(0, '1') → (2, '1', R)`: found a 1 → reject

On input "00":
1. state=0, head=0, tape=['0','0']: read '0' → write '0', move R, state=0
2. state=0, head=1, tape=['0','0']: read '0' → write '0', move R, state=0
3. state=0, head=2, tape=['0','0','_']: read '_' → write '_', move R, state=1
4. state=1 == accept_state → output **accept** ✓

On input "01":
1. state=0, head=0: read '0' → R, state=0
2. state=0, head=1: read '1' → write '1', R, state=2
3. state=2 == reject_state → output **reject** ✓
