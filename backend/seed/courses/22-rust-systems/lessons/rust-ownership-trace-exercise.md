# Ownership Trace Simulator

## Exercise Overview

The Rust borrow checker enforces ownership rules at **compile time**. In this exercise, you will simulate that checker by processing a sequence of ownership operations and determining whether each one is valid or would be rejected by the compiler.

## Ownership Rules Recap

Rust enforces three core rules:

1. Every value has exactly one owner.
2. When the owner goes out of scope, the value is dropped.
3. You can have either **one mutable reference** OR **any number of immutable references** — but never both simultaneously.

## The Five Commands

| Command | Meaning |
|---------|---------|
| `MOVE x y` | Transfer ownership from `x` to `y`. After the move, `x` is invalid. |
| `BORROW x` | Create an immutable `&x`. Valid if `x` is owned and not mutably borrowed. |
| `MUTBORROW x` | Create a mutable `&mut x`. Valid only if no other borrows (mutable or immutable) exist. |
| `DROP name` | Release a borrow or drop an owner. If dropping a borrow, decrement borrow count. |
| `READ x` | Read the value at `x`. Valid if `x` is still owned and not moved. |

## What to Print

For each command, print `OK` if the operation is valid, or `ERROR: <reason>` if it would be rejected. Common error messages:

- `ERROR: a has been moved` — trying to use a moved variable
- `ERROR: cannot mutably borrow b while immutable borrows exist`
- `ERROR: cannot mutably borrow b: already mutably borrowed`
- `ERROR: x is not a valid owner`

## Study Resources

- [The Rust Programming Language, Chapter 4](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html) — the definitive guide to ownership and borrowing
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — Google's free Rust course with clear ownership diagrams
