# Concurrent Task Scheduler Simulator

## Exercise Overview

Rust's concurrency safety rests on two marker traits:

- **`Send`** — a type is safe to **move** to another thread (transfer ownership across a thread boundary)
- **`Sync`** — a type is safe to **share by reference** across threads (i.e., `&T: Send`)

Most types in Rust are automatically `Send + Sync`. Notable exceptions:

| Type | Send? | Sync? | Reason |
|------|-------|-------|--------|
| `Arc<Mutex<T>>` where T: Send | Yes | Yes | Atomic reference counting + locked access |
| `Rc<T>` | No | No | Non-atomic reference count; not thread-safe |
| `String` | Yes | Yes | Owned, no borrows |
| `*mut T` (raw pointer) | No | No | Unsafe; the compiler can't verify safety |
| `MutexGuard<T>` | No | Yes | Must be unlocked on the same thread |

## The Rules in This Exercise

A thread receives a variable in one of two ways:

- **`SPAWN_MOVE`** — the variable's ownership is moved into the new thread. Requires `Send`.
- **`SPAWN_SHARE`** — a reference to the variable is shared with the new thread. Requires `Sync`.

## Why These Rules Matter

Without `Send` and `Sync`, Rust would allow you to send an `Rc<T>` to another thread. Two threads incrementing the same non-atomic reference count is a classic **data race** — undefined behavior in C/C++ that Rust's type system makes impossible at compile time.

## Study Resources

- [The Rust Programming Language, Chapter 16.4](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html) — Send and Sync traits
- [The Rustonomicon: Send and Sync](https://doc.rust-lang.org/nomicon/send-and-sync.html) — formal safety requirements
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — concurrency chapter with worked examples
