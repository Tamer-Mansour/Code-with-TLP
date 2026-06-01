# Hello, Rust

Rust is a systems language with the performance profile of C++ and the safety guarantees of a memory-managed language — but with **no garbage collector**. The compiler enforces memory and thread safety through a unique **ownership** system, checked at compile time.

## Install

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
rustc --version
cargo --version
```

`rustup` manages toolchains; `cargo` is the project + package manager; `rustc` is the compiler. You'll use `cargo` for everything.

## A first project

```bash
cargo new hello
cd hello
cargo run
```

`src/main.rs`:

```rust
fn main() {
    println!("Hello, Rust!");
}
```

`println!` is a **macro** (the `!`), not a function. Don't worry about why yet.

## Cargo essentials

```bash
cargo build              # compile (debug)
cargo build --release    # optimized
cargo run                # build + run
cargo test               # run tests
cargo check              # type-check without producing a binary (fast)
cargo fmt                # format
cargo clippy             # lints
cargo add serde          # add dependency
```

`cargo check` is your fast feedback loop — way faster than `build`, catches most errors.

## Cargo.toml — manifest

```toml
[package]
name = "hello"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }
```

Editions correspond roughly to language-level revisions: 2015 → 2018 → 2021 → 2024 (forthcoming). Old editions still work; new editions enable new syntax.

## What Rust is good for

- Systems / low-level (kernels, embedded, drivers).
- High-performance backends (Discord, Cloudflare).
- CLI tools (`ripgrep`, `bat`, `fd`).
- WebAssembly modules.
- Replacing C / C++ where safety matters (Mozilla, Linux kernel modules).

## What Rust isn't

- A scripting language. The compile-edit cycle is heavier than Python/Go.
- A "let me prototype" language. The borrow checker forces design upfront.
- A first language. Coming from a managed language, the learning curve is real.

## The famous learning curve

Two ideas trip everyone up at first:

1. **Ownership / borrowing.** Variables have a single owner; you can lend references, but the compiler forces you to be precise about lifetime and mutability.
2. **Lifetimes.** A reference must not outlive what it points to — and the compiler verifies it.

Once they click (a few weeks), you'll wonder why other languages don't enforce this.

## Hello world, plus a function

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b              // no semicolon = return value
}

fn main() {
    let x = add(2, 3);
    println!("{}", x);
}
```

Statements end with `;`. Expressions without `;` return values from the enclosing block — including function bodies.
