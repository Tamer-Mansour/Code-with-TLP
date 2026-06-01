# Lifetimes

A **lifetime** is a region of the program during which a reference is valid. The compiler enforces that references never outlive what they point to. Sometimes it can infer them; sometimes you write them explicitly.

## The motivating problem

```rust
fn longest(a: &str, b: &str) -> &str {     // ❌ won't compile
    if a.len() > b.len() { a } else { b }
}
```

The compiler doesn't know whether the return reference borrows from `a` or `b`. Solution: lifetime annotation.

```rust
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}
```

`'a` says: the return reference lives at least as long as both inputs. Now the compiler can verify safe usage.

## Read the syntax

- `&str` — a reference with an inferred (elided) lifetime.
- `&'a str` — a reference with named lifetime `'a`.
- `<'a>` after a function name — declares the lifetime parameter.

Lifetimes are types-of-types — they parameterize a function the same way `T` does.

## Lifetime elision

The compiler infers lifetimes in three common cases — you don't need to write them:

1. Each input reference gets its own lifetime: `fn f(x: &str, y: &str)` → `fn f<'a, 'b>(x: &'a str, y: &'b str)`.
2. If there's exactly one input lifetime, the output gets the same: `fn f(s: &str) -> &str` is OK.
3. If `&self` is an input, the output borrows from `self`.

Most function signatures don't need explicit lifetimes thanks to elision.

## In structs

A struct that holds a reference must declare a lifetime:

```rust
struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn announce(&self, prefix: &str) -> &str {
        self.text
    }
}
```

The struct can't outlive the `&str` it borrows.

## 'static — lives forever

A reference with `'static` lifetime exists for the entire program:

```rust
let s: &'static str = "hello, world";    // string literal
```

String literals are `&'static str`. Some types implement `: 'static` to mean "all references inside last forever" — common for spawned threads.

## When lifetime errors hit

You'll see messages like:

```
error[E0597]: `s` does not live long enough
```

The fix is rarely "add a lifetime annotation." Usually it's one of:

- Return an owned value (`String`) instead of a borrowed one (`&str`).
- Restructure who owns what.
- Use `Rc<T>` or `Arc<T>` for shared ownership.
- Use `Box<T>` to put the data on the heap.

## Owned vs borrowed APIs

A common Rust design choice:

```rust
struct Config {
    path: String,            // owned
}

struct Excerpt<'a> {
    text: &'a str,           // borrowed
}
```

Borrow when:
- The data outlives this struct.
- You want to avoid copies.

Own when:
- The struct will outlive what it'd borrow from.
- You're sending it to another thread.
- Returning from a function that allocated the data.

## A note on async

Async functions can capture references too, and lifetime errors are often more involved in async code. Reach for `Arc` and `'static` more often there; the borrow checker rules don't bend for async.

## When lifetimes click

After a few weeks of writing Rust, lifetimes stop being a mystery — they're how the compiler tells you "this reference could outlive its data." Once you trust that, the safety guarantees are real and zero-cost.
