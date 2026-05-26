# Traffic Light State Machine

Implement a `TrafficLight` class that models a simple traffic light as a state machine.

## States

The light cycles through: `RED -> GREEN -> YELLOW -> RED -> ...`

## Commands

Read `N` on the first line, then `N` commands, one per line:

- `NEXT` — advance to the next state in the cycle.
- `STATE` — print the current state name in uppercase.
- `COUNT` — print how many times `NEXT` has been called so far.
- `RESET` — return to `RED` without incrementing the next-count.

## Initial state

The light starts at `RED` with a count of `0`.

## Example

```
5
STATE
NEXT
NEXT
STATE
COUNT
```

Output:
```
RED
YELLOW
2
```

(`STATE` prints `RED` initially. `NEXT` moves to GREEN, another `NEXT` moves to YELLOW. `STATE` prints `YELLOW`. `COUNT` prints 2.)
