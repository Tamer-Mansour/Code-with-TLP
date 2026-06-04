# Asynchronous Programming in Rust

Rust's async system lets you write concurrent I/O-bound code that looks like sequential code — without the overhead of OS threads. The key insight: `async`/`await` is syntactic sugar that compiles to hand-written state machines.

## The Problem Async Solves

Thread-per-connection server models break down at scale. A thread typically costs 1–8 MB of stack memory; 10,000 concurrent connections means 10–80 GB of RAM just for stacks. Async tasks are far lighter — a Tokio task starts at about 256 bytes.

## `Future`: the Core Trait

Every async value in Rust implements `Future`:

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}

pub enum Poll<T> {
    Ready(T),
    Pending,
}
```

A future is polled: if the work is done, it returns `Ready(value)`; if it's still waiting (e.g., for a network packet), it returns `Pending` and registers a **waker** so it will be polled again when the I/O is ready.

## `async`/`await` Syntax

```rust
async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
    let response = reqwest::get(url).await?;
    let text = response.text().await?;
    Ok(text)
}
```

`async fn` desugars into a function that returns `impl Future<Output = Result<String, ...>>`. The `.await` points are where execution can be suspended and resumed — the compiler converts the function into a state machine enum.

## Futures Need a Runtime

This is a critical point beginners miss: **the Rust standard library provides the `Future` trait but ships with no built-in executor**. A future created by an `async fn` does nothing until something polls it.

```rust
// This does nothing on its own:
let future = fetch_data("https://example.com");

// You need a runtime to drive it:
#[tokio::main]
async fn main() {
    let result = fetch_data("https://example.com").await;
}
```

The most widely used runtime is **Tokio**. `async-std` is another option.

## Tokio Basics

```rust
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let task1 = tokio::spawn(async {
        sleep(Duration::from_millis(100)).await;
        println!("task 1 done");
    });

    let task2 = tokio::spawn(async {
        println!("task 2 done immediately");
    });

    let _ = tokio::join!(task1, task2);
}
```

`tokio::spawn` creates an independent task that runs concurrently. `tokio::join!` awaits multiple futures concurrently — both run in parallel; neither blocks the other.

## `Pin<T>` and Self-Referential Futures

When an `async fn` awaits something, the compiler stores all local variables in a struct (the state machine). If a local variable holds a reference to another local variable, the struct becomes **self-referential** — moving it in memory would invalidate the internal pointer.

`Pin<&mut T>` prevents a value from being moved:

```rust
use std::pin::Pin;
use std::future::Future;

fn run<F: Future>(future: F) -> F::Output {
    // A real executor would poll the future here via Pin
    todo!()
}
```

In practice, you rarely write `Pin` code directly — the runtime handles it. Understanding it matters when implementing custom `Future` types or working with self-referential data.

## Async I/O: Non-Blocking Networking

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;

    loop {
        let (mut socket, addr) = listener.accept().await?;
        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            let n = socket.read(&mut buf).await.unwrap();
            socket.write_all(&buf[..n]).await.unwrap();
        });
    }
}
```

Each connection gets its own lightweight async task. Thousands of connections share a small thread pool (usually one thread per CPU core).

## Cancellation and Structured Concurrency

Dropping a future cancels it — the state machine is dropped without completing. This is powerful but dangerous if a future has partial side effects:

```rust
// tokio::select! runs both futures, returns the first to complete,
// and CANCELS the other.
tokio::select! {
    result = long_operation() => { handle(result) }
    _ = tokio::time::sleep(Duration::from_secs(5)) => {
        println!("timed out");
    }
}
```

A future is **cancellation-safe** if it can be dropped at any await point without leaving inconsistent state. `tokio::sync::Mutex` is cancellation-safe; `std::sync::MutexGuard` held across `.await` is not — it blocks the thread.

## Sync vs Async: When to Use Each

| Use threads (`std::thread`) | Use async (`tokio`) |
|-----------------------------|---------------------|
| CPU-bound work | I/O-bound work |
| Simple one-off background tasks | High-concurrency servers |
| Libraries with no async dependency | Code that already uses async |
| You need blocking APIs | You can use non-blocking APIs |

## Further Reading

- [Asynchronous Programming in Rust (The Async Book)](https://rust-lang.github.io/async-book/) — the official async Rust guide: Futures, executors, Pin, Tokio internals, and best practices
- [The Rust Programming Language, Chapter 17](https://doc.rust-lang.org/book/ch17-00-async-await.html) — async/await chapter in the official book (added in 2024 edition)
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial) — official hands-on tutorial for building async apps
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — async chapter with interactive examples
