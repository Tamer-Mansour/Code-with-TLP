# Variables and Types in Rust

Rust is a statically typed language — every variable has a type known at compile time. The compiler is usually smart enough to infer types from context, so you don't need to annotate everything.

## `let` bindings and immutability

By default, all variables in Rust are **immutable**. You must opt into mutability with `mut`.

```rust
let x = 5;          // immutable
x = 6;              // ❌ error: cannot assign twice to immutable variable

let mut y = 5;
y = 6;              // ✅ OK
```

This default makes code safer and easier to reason about — if a value never changes, the compiler can prove it and flag unexpected mutations.

## Scalar types

| Type family  | Examples                           | Notes                              |
|--------------|------------------------------------|------------------------------------|
| Integer      | `i8`, `i16`, `i32`, `i64`, `i128`, `isize` | Signed; `isize` is pointer-sized  |
| Unsigned int | `u8`, `u16`, `u32`, `u64`, `u128`, `usize` | `usize` used for indices/lengths  |
| Float        | `f32`, `f64`                       | IEEE-754; default is `f64`         |
| Boolean      | `bool`                             | `true` / `false`                   |
| Character    | `char`                             | Unicode scalar (4 bytes)           |

```rust
let n: i32 = -42;
let big: u64 = 1_000_000;   // underscores for readability
let pi: f64 = 3.14159;
let flag: bool = true;
let heart: char = '♥';
```

## Type inference

The compiler infers the type from how you use the value:

```rust
let mut v = Vec::new();      // compiler doesn't know the type yet
v.push(1_u32);               // now it knows: Vec<u32>
```

When inference fails, add a type annotation or a suffix literal (`42_u8`, `3.0_f32`).

## Shadowing

You can re-declare a variable with the same name using a new `let`. This is called **shadowing** and is different from mutation.

```rust
let x = 5;
let x = x + 1;       // shadows the previous x
let x = x * 2;       // shadows again
println!("{}", x);   // 12
```

Shadowing lets you reuse a name while changing the type — useful after parsing a string into a number:

```rust
let input = "42";
let input: u32 = input.parse().unwrap();   // same name, different type
```

## Compound types

### Tuples — fixed-length, mixed types

```rust
let point: (i32, i32) = (10, 20);
let (x, y) = point;            // destructuring
println!("{}, {}", x, y);      // 10, 20
println!("{}", point.0);       // 10 — field access by index
```

### Arrays — fixed-length, same type, stack-allocated

```rust
let a: [i32; 5] = [1, 2, 3, 4, 5];
println!("{}", a[2]);          // 3
let zeros = [0_u8; 128];       // 128 zero bytes
```

For growable sequences, use `Vec<T>` (covered in the Collections module).

## Constants and statics

```rust
const MAX_POINTS: u32 = 100_000;   // always typed, computed at compile time
static GREETING: &str = "hello";   // lives for the whole program
```

Constants are inlined at compile time; statics have a fixed address in memory.

## Practical tips

- Use `i32` and `f64` as the default integer and float types unless you have a specific reason.
- Use `usize` for all slice indices and lengths.
- Prefer immutable bindings; add `mut` only when you truly mutate.
- Use `_` as a prefix for intentionally unused variables to silence the compiler warning: `let _unused = 0;`.
