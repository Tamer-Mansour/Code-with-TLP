# Closures in Rust

A closure is an anonymous function that can **capture variables from its surrounding environment**. Closures are the glue between the iterator adapters you saw in the last lesson and real data.

## Basic syntax

```rust
// Regular function
fn add_one(x: i32) -> i32 { x + 1 }

// Equivalent closure
let add_one = |x: i32| -> i32 { x + 1 };

// Type inference — Rust infers parameter and return types
let add_one = |x| x + 1;

// Multi-line closure with a block
let describe = |n: i32| {
    if n > 0 { "positive" } else { "non-positive" }
};
```

The `|params|` syntax replaces `fn name(params)`. Types are usually inferred.

## Capturing the environment

Unlike regular functions, closures can reach into the scope where they were defined:

```rust
let threshold = 5;

// Captures `threshold` by reference (immutable borrow)
let is_big = |x| x > threshold;

println!("{}", is_big(3));    // false
println!("{}", is_big(10));   // true
```

The compiler chooses the least-restrictive capture mode automatically:

| Capture mode      | How                    | Trait     |
|-------------------|------------------------|-----------|
| Immutable borrow  | `&T`                   | `Fn`      |
| Mutable borrow    | `&mut T`               | `FnMut`   |
| Take ownership    | move semantics         | `FnOnce`  |

## The `move` keyword

Force the closure to take ownership of all captured variables. Necessary when the closure outlives the current scope — especially common with threads.

```rust
let name = String::from("Alice");

// Without `move`, `name` is borrowed — but the closure might outlive `name`
let greet = move || println!("Hello, {}!", name);
// `name` has been moved into the closure; the original binding is gone.

greet();   // "Hello, Alice!"
```

## `Fn`, `FnMut`, `FnOnce`

These traits describe how a closure uses its captured environment:

- **`Fn`** — can be called any number of times; only reads captured values.
- **`FnMut`** — can be called any number of times; mutates captured values.
- **`FnOnce`** — can be called only once; consumes (moves) captured values.

Every closure automatically implements the most general trait that applies. A `Fn` is also `FnMut` and `FnOnce`.

```rust
// Accepts any callable that takes i32 and returns i32
fn apply<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(x)
}

let double = |x| x * 2;
println!("{}", apply(double, 5));   // 10
```

## Returning closures

Closures have unique anonymous types; you can't name them in a return position. Use `impl Fn(…)` or box them:

```rust
// Return a closure with impl Trait (zero-cost)
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

let add5 = make_adder(5);
println!("{}", add5(10));   // 15
println!("{}", add5(20));   // 25
```

If you need to store closures of different types together, use `Box<dyn Fn(…)>`:

```rust
fn make_adder(n: i32) -> Box<dyn Fn(i32) -> i32> {
    Box::new(move |x| x + n)
}
```

## Closures with iterators in practice

```rust
let data = vec![3, 1, 4, 1, 5, 9, 2, 6];
let min_threshold = 4;

let big_squares: Vec<i32> = data.iter()
    .filter(|&&x| x >= min_threshold)   // captures min_threshold
    .map(|&x| x * x)
    .collect();

println!("{:?}", big_squares);   // [16, 25, 81, 36]
```

The closure in `filter` borrows `min_threshold` immutably — safe, simple, zero allocation.

## Tips

- Let the compiler infer closure types; only annotate when there's ambiguity.
- Prefer `|x| …` over `move |x| …` unless the closure needs to outlive the current scope.
- When a function parameter is `impl Fn(…)`, the caller can pass a closure or a named function — they are interchangeable.
