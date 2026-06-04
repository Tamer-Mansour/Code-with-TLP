# Transaction Rollback Simulator

## Problem

Simulate a simple in-memory database transaction log. Process a sequence of commands and output the final table state.

**Commands:**

| Command                    | Effect                                                         |
|----------------------------|----------------------------------------------------------------|
| `BEGIN`                    | Start a transaction; initialize an empty table                 |
| `INSERT name amount`       | Add or overwrite the entry for `name` with `amount` (integer)  |
| `DELETE name`              | Remove `name` from the table (no-op if not present)            |
| `SAVEPOINT`                | Save current table state as a checkpoint                       |
| `ROLLBACK_TO_SAVEPOINT`    | Restore table to last SAVEPOINT state (or empty if no savepoint exists) |
| `COMMIT`                   | Finalize changes; clear the savepoint                          |
| `ROLLBACK`                 | Discard all changes since BEGIN; empty the table               |

**Input:** One command per line (no blank lines). There is exactly one `BEGIN` at the start.

**Output:** After all commands are processed, print the final table contents sorted by `name` ascending, one entry per line as `name amount`. If the table is empty, print `EMPTY`.

## Example

**Input:**
```
BEGIN
INSERT Alice 1000
INSERT Bob 2000
SAVEPOINT
INSERT Carol 3000
DELETE Bob
ROLLBACK_TO_SAVEPOINT
INSERT Dave 4000
COMMIT
```

**Output:**
```
Alice 1000
Bob 2000
Dave 4000
```

**Explanation:**
- After INSERT Alice and Bob: `{Alice: 1000, Bob: 2000}`
- SAVEPOINT saves this state
- INSERT Carol, DELETE Bob: `{Alice: 1000, Carol: 3000}`
- ROLLBACK_TO_SAVEPOINT restores: `{Alice: 1000, Bob: 2000}`
- INSERT Dave: `{Alice: 1000, Bob: 2000, Dave: 4000}`
- COMMIT finalizes

## Constraints

- Input always starts with `BEGIN`
- `1 <= number of commands <= 100`
- `name` values are alphabetic strings with no spaces
- `amount` values are positive integers
- There is at most one active savepoint at a time (each `SAVEPOINT` overwrites the previous one)
