# Calculator with Undo/Redo (Command Pattern)

Implement a calculator that supports arithmetic commands plus undo and redo.

## State

A single integer register, starting at `0`.

## Commands

Read `N` on the first line, then `N` commands:

- `ADD <n>` — add integer `n` to the register.
- `SUB <n>` — subtract integer `n` from the register.
- `MUL <n>` — multiply the register by integer `n`.
- `VALUE` — print the current register value.
- `UNDO` — undo the last operation. If nothing to undo, print `NOTHING TO UNDO`.
- `REDO` — redo the last undone operation. If nothing to redo, print `NOTHING TO REDO`.

## Notes

- `UNDO`/`REDO` do not print the register value by themselves.
- A new `ADD`/`SUB`/`MUL` after `UNDO` clears the redo stack.

## Example

```
8
ADD 10
MUL 3
VALUE
UNDO
VALUE
REDO
VALUE
UNDO
```

Output:
```
30
10
30
```

(ADD 10 → 10. MUL 3 → 30. VALUE → 30. UNDO undoes MUL 3 → 10. VALUE → 10. REDO redoes MUL 3 → 30. VALUE → 30. UNDO undoes MUL 3 again → 10.)
