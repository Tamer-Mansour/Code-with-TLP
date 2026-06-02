# Exercise: Simulate Reference Counting and Cycle Leaks

In this exercise you will implement a **simplified reference-counting allocator** in Python that mirrors how `shared_ptr` and `weak_ptr` track object lifetimes. You will then use it to demonstrate both correct cleanup and the cycle leak that `weak_ptr` was designed to prevent.

## What You Will Implement

You will write a program that reads a sequence of commands and simulates a mini reference-counting system:

- `ALLOC <id>` — create a new object with the given string id. Strong count starts at 1, weak count at 0.
- `SHARE <id>` — add a strong reference to object `id` (increment strong count).
- `WEAK <id>` — add a weak reference to object `id` (increment weak count only).
- `RELEASE <id>` — remove one strong reference. If strong count reaches 0, destroy the object and print a destruction message. Then decrement weak count by 1 (the implicit +1 held while strong count > 0); if weak count also reaches 0 free the control block.
- `DROP_WEAK <id>` — remove one weak reference. If strong count is already 0 and weak count reaches 0, free the control block.
- `STATUS <id>` — print `<id>: strong=<n> weak=<n>` or `<id>: freed` if the control block is gone.

Each command is on its own line. Process them in order.

## Expected Output Format

- `ALLOC x` prints: `allocated x`
- `SHARE x` prints: `shared x (strong=N)`
- `WEAK x` prints: `weak ref x (weak=N)`
- `RELEASE x` when strong count drops to 0: print `destroyed x`, then check if weak count (after decrementing the implicit hold) is 0 and if so print `freed x`
- `RELEASE x` when strong count stays above 0: print `released x (strong=N)`
- `DROP_WEAK x` when both counts reach 0 after decrement: print `freed x`
- `DROP_WEAK x` otherwise: print `dropped weak x (weak=N)`
- `STATUS x`: print `x: strong=N weak=N` or `x: freed`

## Skills Practiced

- Tracing the lifecycle of `shared_ptr` and `weak_ptr` through reference count transitions.
- Identifying the exact moment of object destruction (strong count hits 0) versus control block deallocation (weak count hits 0).
- Recognizing cycle leaks: if two objects hold strong references to each other and you `RELEASE` the external handles, both will still have `strong=1` — they never get destroyed.

## Sample Session

```
ALLOC node_a
ALLOC node_b
SHARE node_a    ← simulate a->next = b (node_a holds strong ref to node_b... via node_b's count)
SHARE node_b    ← simulate b->next = a
RELEASE node_a  ← external handle released
RELEASE node_b  ← external handle released — both still alive, cycle!
STATUS node_a
STATUS node_b
```

Expected output for the above:

```
allocated node_a
allocated node_b
shared node_a (strong=2)
shared node_b (strong=2)
released node_a (strong=1)
released node_b (strong=1)
node_a: strong=1 weak=0
node_b: strong=1 weak=0
```

Both objects remain alive with `strong=1` — the classic cycle leak.
