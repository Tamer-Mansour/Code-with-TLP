# Lifetimes Deep Dive

Lifetimes are Rust's compile-time mechanism for proving that references are always valid. They are **entirely erased at runtime** — no code is generated, no overhead incurred. Every lifetime annotation is a constraint the compiler verifies and then discards.

## What a Lifetime Actually Is

A lifetime is a named region of code during which a reference must be valid. Think of it as a label you attach to a reference, telling the compiler "this reference is only valid between points A and B in the program."

```rust
// The lifetime 'a says: the return reference is valid
// for at least as long as both input references.
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Without `'a`, the compiler cannot know whether the returned reference comes from `x` or `y`, so it cannot check that the caller keeps the right variable alive long enough.

## Lifetime Elision Rules

The compiler can infer lifetimes in three patterns so you don't have to write them explicitly:

**Rule 1** — Each input reference gets its own unique lifetime:
```rust
fn first_word(s: &str) -> &str  // elided
// expands to:
fn first_word<'a>(s: &'a str) -> &'a str
```

**Rule 2** — If there is exactly one input reference, the output borrows from it:
```rust
fn trim(s: &str) -> &str  // OK — single input, output shares its lifetime
```

**Rule 3** — If one of the inputs is `&self` or `&mut self`, the output borrows from `self`:
```rust
impl Parser {
    fn next_token(&self) -> &str { ... }  // output borrows from self
}
```

When none of these three rules apply and there are multiple input lifetimes, you must annotate explicitly.

## Lifetime Subtyping

A lifetime `'long: 'short` means `'long` **outlives** `'short`. The colon reads "outlives."

```rust
fn first<'short, 'long: 'short>(
    x: &'short str,
    y: &'long str,
) -> &'short str {
    x
}
```

This is **variance**: `'long` is a subtype of `'short` because a reference valid for a longer region can always substitute for one valid for a shorter region.

## Lifetime Parameters on Structs

When a struct holds a reference, the struct must not outlive what it borrows:

```rust
struct StrSplit<'haystack, 'delimiter> {
    remainder: &'haystack str,
    delimiter: &'delimiter str,
}
```

The two lifetime parameters say the `StrSplit` value is only valid as long as both the haystack string and the delimiter string are alive.

## The `'static` Lifetime

`'static` means valid for the entire program. Two distinct uses:

**1. String literals** — compiled into the binary's read-only segment:
```rust
let greeting: &'static str = "hello, world";
```

**2. Owned types satisfy `T: 'static`** — a bound that says "this type contains no short-lived borrows":
```rust
fn spawn_task<F: FnOnce() + Send + 'static>(f: F) {
    std::thread::spawn(f);
}
```

An owned `String` satisfies `'static` even though it lives on the heap, because it contains no borrowed references. This is a common source of confusion: `'static` is a bound on lifetimes embedded in a type, not a claim about storage class.

## Practical Lifetime Patterns

**Return owned instead of borrowing** — the most common fix:
```rust
// Instead of borrowing with complex lifetime constraints:
fn get_name<'a>(&'a self, ...) -> &'a str { ... }
// Consider returning owned when the data can be cloned cheaply:
fn get_name(&self) -> String { self.name.clone() }
```

**`Cow<'a, str>`** — borrow when you can, own when you must:
```rust
use std::borrow::Cow;

fn normalize(s: &str) -> Cow<str> {
    if s.contains(' ') {
        Cow::Owned(s.replace(' ', "_"))
    } else {
        Cow::Borrowed(s)
    }
}
```

**`Arc<T>` for cross-thread lifetimes** — when the borrow checker rejects sharing a reference across threads, `Arc` gives shared ownership without lifetimes:
```rust
let data = Arc::new(load_config());
let data_clone = Arc::clone(&data);
thread::spawn(move || process(data_clone));
```

## Variance in Depth

Rust has three flavors of variance for lifetime parameters:

| Variance | Meaning | Example |
|----------|---------|---------|
| Covariant | `'long` can substitute for `'short` | `&'a T` is covariant over `'a` |
| Contravariant | `'short` can substitute for `'long` | `fn(&'a T)` is contravariant over `'a` |
| Invariant | No substitution allowed | `&'a mut T` is invariant over `'a` |

`&mut T` is invariant over `T` — you cannot coerce `&mut &'short str` to `&mut &'long str`. This prevents a subtle class of soundness bugs.

## Common Error Messages and Fixes

```
error[E0597]: `s` does not live long enough
```
The reference outlives its referent. Fix: move data ownership to the same scope, or return an owned value.

```
error[E0106]: missing lifetime specifier
```
The compiler cannot apply elision rules. Fix: add an explicit lifetime annotation to the return type.

```
error[E0495]: cannot infer an appropriate lifetime for borrow expression
```
The lifetime of one reference is being constrained by conflicting requirements. Fix: add lifetime subtyping or restructure ownership.

## Further Reading

- [The Rust Programming Language, Chapter 10.3](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) — official lifetime reference
- [The Rustonomicon: Lifetimes](https://doc.rust-lang.org/nomicon/lifetimes.html) — subtyping, variance, and advanced patterns
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — Google's free course with interactive lifetime exercises
