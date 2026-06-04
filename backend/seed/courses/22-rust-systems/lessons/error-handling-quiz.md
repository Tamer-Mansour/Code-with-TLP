# Quiz - Error Handling and Lifetimes

Test your understanding of Result, Option, the ? operator, custom errors, and lifetime annotations.

## Question 1

What does the `?` operator do when used on a `Result<T, E>` expression?

- [ ] It unwraps the value, panicking if it is an `Err`
- [x] If the value is `Ok(v)`, it extracts `v`; if it is `Err(e)`, it converts `e` using `From` and returns `Err` from the enclosing function
- [ ] It ignores the error and returns `None`
- [ ] It logs the error and continues execution

## Question 2

What is the difference between `unwrap()` and `expect("msg")` on a `Result`?

- [ ] `unwrap()` returns the error; `expect()` panics
- [ ] They are identical in behavior
- [x] Both panic on `Err`, but `expect()` includes your custom message in the panic output, making debugging easier
- [ ] `expect()` returns a `Result`; `unwrap()` returns the inner value

## Question 3

Which crate provides the `#[derive(Error)]` macro for ergonomic custom error types?

- [ ] `anyhow`
- [x] `thiserror`
- [ ] `serde`
- [ ] `failure`

## Question 4

What does `anyhow::Result<T>` give you compared to `std::result::Result<T, E>`?

- [x] A convenience type where the error is a heap-allocated, dynamically-typed error value — useful in application code where you don't need to enumerate error variants
- [ ] A result type that never panics
- [ ] A result that automatically retries on failure
- [ ] A type that wraps both `Ok` and `Err` as `Option`

## Question 5

When should you use `panic!` vs `Result`?

- [ ] Always use `panic!` — it gives better error messages
- [ ] Always use `Result` — panics are never appropriate in Rust
- [x] Use `Result` for expected, recoverable failures (bad input, I/O errors). Use `panic!` for unrecoverable programmer errors or violated invariants that indicate a bug.
- [ ] Use `panic!` in library code; use `Result` in application code

## Question 6

What is a **dangling reference** in the context of Rust lifetimes?

- [ ] A reference to a value that is `None`
- [x] A reference that outlives the value it points to — the variable has been dropped but the reference still exists
- [ ] A reference that has been moved to another scope
- [ ] A mutable reference that is no longer mutable

## Question 7

What is lifetime **elision**?

- [ ] The process of removing unused lifetime parameters from the binary
- [x] A set of compiler rules that allow you to omit explicit lifetime annotations in common, unambiguous cases
- [ ] Automatically shortening lifetimes to the minimum required
- [ ] The garbage collection mechanism Rust uses for references

## Question 8

What does `'static` mean as a **trait bound** (e.g., `T: 'static`)?

- [ ] The value must be allocated in static memory (the BSS or data segment)
- [ ] The value must live for exactly the duration of the program
- [x] The type contains no borrowed references with a lifetime shorter than the entire program duration; owned types like `String` satisfy this even though they are heap-allocated
- [ ] The value cannot be dropped
