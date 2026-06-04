# Trait Dispatch Resolver

## Exercise Overview

Rust's trait system supports two fundamentally different dispatch strategies:

**Static dispatch** (generics with trait bounds): the compiler generates a separate copy of the function for each concrete type — a process called **monomorphization**. Zero runtime overhead; the correct method is determined at compile time.

**Dynamic dispatch** (`dyn Trait`): the compiler emits a vtable — a table of function pointers for the trait's methods. At runtime, a fat pointer carries both the data address and the vtable address. This enables heterogeneous collections but costs one pointer indirection per method call.

## Key Rule: Object Safety

A trait can only be used as `dyn Trait` if it is **object-safe**:
- No methods return `Self`
- No methods have generic type parameters
- No `Sized` supertrait bound

## Dispatch Rules in This Problem

- `STATIC Trait Type` — type must have a registered `implements Trait` declaration
- `DYNAMIC Trait Type1,Type2,...` — every type in the list must implement the trait

## Study Resources

- [The Rust Programming Language, Chapter 17](https://doc.rust-lang.org/book/ch17-02-trait-objects.html) — Trait objects and dynamic dispatch
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) — Deep dive into vtables, variance, and object safety
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — Google's free course with dispatch examples
