# Concurrent Task Scheduler Simulator

Simulate a Rust thread scheduler that enforces `Send` and `Sync` rules. Determine whether each thread spawn operation is valid.

## Input Format

Each line is one command:

- `DECLARE <var> <type> <property>` — declare a variable with a concurrency property
  - `property` is one of: `SEND_SYNC`, `SEND`, `SYNC`, `NEITHER`
- `SPAWN_MOVE <thread_id> <var>` — move `var` into a new thread (requires `Send`)
- `SPAWN_SHARE <thread_id> <var>` — share `&var` with a new thread (requires `Sync`)

## Output

For `SPAWN_MOVE` and `SPAWN_SHARE` commands only, print one line each:

- `OK` — if the operation is permitted by the Send/Sync rules
- `ERROR: <var> is not Send` — if SPAWN_MOVE but the type is not Send
- `ERROR: <var> is not Sync` — if SPAWN_SHARE but the type is not Sync

## Sample Input

```
DECLARE data ArcMutex SEND_SYNC
DECLARE counter Rc NEITHER
DECLARE msg String SEND_SYNC
DECLARE raw RawPtr SEND
SPAWN_MOVE t1 data
SPAWN_MOVE t2 counter
SPAWN_SHARE t3 msg
SPAWN_SHARE t4 raw
```

## Sample Output

```
OK
ERROR: counter is not Send
OK
ERROR: raw is not Sync
```

## Constraints

- `1 <= number of commands <= 100`
- All `SPAWN_*` commands reference previously declared variables
- Type names and variable names are single words
- Property is always one of the four values listed above
