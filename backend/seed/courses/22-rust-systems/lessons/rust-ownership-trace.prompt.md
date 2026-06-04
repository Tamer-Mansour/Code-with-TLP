# Ownership Trace Simulator

Given a sequence of Rust-like ownership operations, simulate whether each operation is valid or would produce a compile error under Rust's borrow-checker rules.

## Commands

Each line of input is one command:

- `MOVE x y` — move the value from variable `x` into `y`. After the move, `x` is invalid and cannot be used.
- `BORROW x` — create an immutable borrow of `x`. Valid if `x` is an owner and not currently mutably borrowed.
- `MUTBORROW x` — create a mutable borrow of `x`. Valid only if no other borrows (immutable or mutable) currently exist for `x`.
- `DROP name` — drop the borrow or owner named by the most recently assigned borrow handle, or drop the owner `name`. Borrows are assigned internal names `borrow1`, `borrow2`, etc. in the order they are created.
- `READ x` — read the value at `x`. Valid if `x` is still owned (not moved or dropped).

All single lowercase letters (`a`–`j`) start as owned variables.

## Output

For each command, print exactly one line: `OK` if the operation is valid, or `ERROR: <reason>` if it would be rejected.

## Sample Input

```
MOVE a b
READ b
READ a
BORROW b
BORROW b
MUTBORROW b
DROP borrow1
DROP borrow2
MUTBORROW b
READ b
```

## Sample Output

```
OK
OK
ERROR: a has been moved
OK
OK
ERROR: cannot mutably borrow b while immutable borrows exist
OK
OK
OK
OK
```

## Constraints

- Input ends at EOF.
- Variable names are single lowercase letters (initially owned) or borrow handles (`borrow1`, `borrow2`, ...).
- At most 100 commands per test case.
