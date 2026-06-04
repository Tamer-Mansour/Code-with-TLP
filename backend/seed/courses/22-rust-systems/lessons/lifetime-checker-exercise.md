# Lifetime Region Checker

## Exercise Overview

The Rust borrow checker validates references by tracking **lifetime regions** — the spans of code during which each reference must remain valid. A reference becomes a **dangling reference** if it outlives the variable it borrows from.

## The Core Rule

For a reference to be valid, the **variable it borrows must be alive for the entire duration the reference exists**. In terms of line ranges:

```
variable.start_line <= reference.start_line
AND
variable.end_line >= reference.end_line
```

If both conditions hold, the reference is `VALID`. Otherwise, it is `DANGLING`.

## Example

```rust
let x = String::from("hello");   // alive: lines 1–10
{
    let ref1 = &x;               // alive: lines 3–8  → VALID (x covers 3–8)
    let y = String::from("world"); // alive: lines 5–7
    let ref2 = &y;               // alive: lines 6–9  → DANGLING (y ends at 7, ref ends at 9)
}
```

## Study Resources

- [The Rust Programming Language, Chapter 10.3](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) — lifetime syntax and rules
- [The Rustonomicon: Lifetimes](https://doc.rust-lang.org/nomicon/lifetimes.html) — formal treatment of lifetime regions
- [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/) — lifetime rules in async contexts (advanced)
