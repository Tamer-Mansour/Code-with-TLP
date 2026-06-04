# Reference Counting Simulation

In this exercise you will simulate the reference counting behavior that `std::shared_ptr` performs internally. Understanding the mechanics of reference counting at this level reveals exactly why shared ownership has a real cost and when a dangling reference is impossible.

## What You Are Building

Given a stream of commands on stdin, maintain a table of handles and objects. Track the reference count of each object. Print `DESTROYED obj_id` when a count drops to zero.

See the prompt for the full command set and output format.

## Key Concepts Exercised

- **Shared ownership:** Multiple handles can point to the same object. The object lives as long as at least one handle exists.
- **Reference counting invariant:** Count equals the number of live handles. Every `CREATE` starts at 1; every `COPY` adds 1; every `DROP` subtracts 1.
- **Deterministic destruction:** When count hits zero the object is immediately destroyed — not deferred, not garbage-collected.

## Suggested Data Structures

```python
handle_to_obj = {}   # handle_name -> object_id
ref_counts    = {}   # object_id   -> int
```

## Reference: C++ Core Guidelines

The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), rule **R.20**, states:

> Use `unique_ptr` or `shared_ptr` to represent ownership.

And rule **R.21**:

> Prefer `unique_ptr` over `shared_ptr` unless you need to share ownership.

This exercise makes clear *why*: every `COPY` increments the count (an atomic operation in real `shared_ptr`), and every `DROP` decrements it. That cost is zero for `unique_ptr` because there is never more than one handle.
