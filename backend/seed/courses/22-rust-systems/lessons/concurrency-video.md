# Rust Concurrency — Video Overview

This video demonstrates Rust's concurrency primitives in practice: spawning threads, communicating via channels, and safely sharing state with `Arc<Mutex<T>>`.

**Key takeaways:**

- The Rust type system makes data races a compile-time error through the `Send` and `Sync` marker traits.
- `mpsc::channel` is the idiomatic way to pass ownership of data between threads.
- `Arc<Mutex<T>>` gives you safe shared mutable state; the `MutexGuard` automatically releases the lock when it goes out of scope.
- For CPU-bound parallel work, the `rayon` crate provides a parallel iterator API that looks identical to the standard iterator API.
- For I/O-bound concurrency at scale, `async`/`await` with the `tokio` runtime is the standard choice in production Rust.
