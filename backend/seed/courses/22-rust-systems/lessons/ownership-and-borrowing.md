# Ownership and Borrowing

Rust's signature concept. Every value has a single **owner**, and the compiler tracks who owns what, when it's borrowed, and when it goes out of scope.

## The three rules

1. Every value has one owner.
2. When the owner goes out of scope, the value is **dropped** (memory freed).
3. There can be **one mutable** reference OR **any number of immutable** references — never both at the same time.

## Move semantics

```rust
let s1 = String::from("hello");
let s2 = s1;          // s1 is MOVED into s2
println!("{}", s1);   // ❌ compile error — s1 no longer valid
```

For types stored on the heap (like `String`), assignment **moves** ownership. The old name is invalidated.

For `Copy` types (most primitives), assignment copies:

```rust
let x = 5;
let y = x;            // x is still valid — i32 is Copy
println!("{} {}", x, y);
```

## Cloning

```rust
let s1 = String::from("hello");
let s2 = s1.clone();      // deep copy; both valid
```

Explicit. Rust never silently copies expensive resources.

## Borrowing

References let you read or mutate a value without owning it.

```rust
fn len(s: &String) -> usize {
    s.len()
}

let s = String::from("hello");
let n = len(&s);          // immutable borrow
println!("{} has length {}", s, n);
```

`&s` is an immutable reference. The function reads but doesn't own.

## Mutable borrowing

```rust
fn add_exclamation(s: &mut String) {
    s.push_str("!");
}

let mut s = String::from("hello");
add_exclamation(&mut s);
println!("{}", s);     // "hello!"
```

You can have **one** mutable reference at a time, and no immutable references concurrently.

## The borrow checker

```rust
let mut s = String::from("hello");
let r1 = &s;
let r2 = &s;
let r3 = &mut s;     // ❌ can't borrow as mut while immutable borrows exist
println!("{} {} {}", r1, r2, r3);
```

The borrow checker stops data races at compile time. Once you reorganize for it, the same code works at runtime with zero overhead.

## Non-Lexical Lifetimes (NLL)

The compiler is smart about when a borrow actually ends:

```rust
let mut s = String::from("hello");
let r1 = &s;
println!("{}", r1);     // last use of r1
let r3 = &mut s;        // OK now — r1 is "dead"
println!("{}", r3);
```

## Slices

A slice is a borrowed view into a contiguous sequence:

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];
let world: &str = &s[6..];
```

`&str` is the universal slice type for strings; `String` is the owned, growable variant.

## Why this exists

C and C++ leave memory management to convention. Use-after-free, double-free, dangling pointers, data races — all run-time bugs in those languages. Rust catches every one of these at **compile time**, and produces machine code as fast as C without garbage collection overhead.

The cost: you spend more time satisfying the compiler upfront. The trade pays back massively in production reliability.

## Tip for new learners

When the borrow checker rejects your code, the fix is almost never "add `.clone()` to everything." Step back and ask: who owns this data? When does it need to live? Often the cleanest fix is to restructure ownership rather than fight the checker.
