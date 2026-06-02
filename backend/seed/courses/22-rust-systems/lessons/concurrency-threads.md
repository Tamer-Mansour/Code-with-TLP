# Concurrency with Threads

Rust's fearless concurrency story rests on the same ownership rules you already know: data races are a **compile-time error**, not a runtime surprise.

## Spawning threads

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    for i in 1..=5 {
        println!("hi from thread, iteration {}", i);
        thread::sleep(Duration::from_millis(1));
    }
});

for i in 1..=3 {
    println!("hi from main, iteration {}", i);
    thread::sleep(Duration::from_millis(1));
}

handle.join().unwrap();   // wait for the spawned thread to finish
```

`thread::spawn` returns a `JoinHandle<T>`. Call `.join()` to block until the thread completes and retrieve its return value (or propagate a panic).

## Moving data into threads with `move`

The closure passed to `thread::spawn` must be `'static` — it cannot borrow from the current frame because the thread might outlive it. Use `move` to transfer ownership:

```rust
let msg = String::from("hello from thread");

let handle = thread::spawn(move || {
    println!("{}", msg);   // msg is owned by the closure now
});

handle.join().unwrap();
```

## Message passing with channels (`mpsc`)

Rust's standard library provides **multi-producer, single-consumer** channels.

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

thread::spawn(move || {
    let val = String::from("payload");
    tx.send(val).unwrap();
    // val is moved; we can't use it after send
});

let received = rx.recv().unwrap();   // blocks until a message arrives
println!("received: {}", received);
```

### Multiple senders

```rust
let (tx, rx) = mpsc::channel();
let tx2 = tx.clone();    // clone the sender; single receiver

thread::spawn(move || tx.send(1).unwrap());
thread::spawn(move || tx2.send(2).unwrap());

for msg in rx {          // iterate until all senders are dropped
    println!("{}", msg);
}
```

## Shared state with `Mutex<T>` and `Arc<T>`

When threads must share mutable data:

- `Mutex<T>` — mutual exclusion lock; only one thread holds the lock at a time.
- `Arc<T>` — atomic reference counting; shared ownership across threads.

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0_i32));
let mut handles = Vec::new();

for _ in 0..8 {
    let c = Arc::clone(&counter);
    let h = thread::spawn(move || {
        let mut guard = c.lock().unwrap();
        *guard += 1;
    });
    handles.push(h);
}

for h in handles {
    h.join().unwrap();
}

println!("counter = {}", *counter.lock().unwrap());   // 8
```

`Arc::clone` increments a reference count (atomically). `Mutex::lock` blocks until the lock is free and returns a `MutexGuard` — when the guard is dropped, the lock is released automatically (RAII).

## `Send` and `Sync` traits

These marker traits are the compile-time enforcement:

| Trait  | Meaning                                               |
|--------|-------------------------------------------------------|
| `Send` | The type can be transferred to another thread          |
| `Sync` | A `&T` can be shared across threads (`T: Sync` ⟺ `&T: Send`) |

Most types are `Send + Sync` automatically. Raw pointers and types containing `Rc<T>` are not — the compiler stops you from sending them across thread boundaries.

## Choosing the right primitive

| Scenario                               | Tool              |
|----------------------------------------|-------------------|
| Fire-and-forget background work        | `thread::spawn`   |
| Pass values between threads            | `mpsc::channel`   |
| Share mutable state safely             | `Arc<Mutex<T>>`   |
| Read-heavy shared state                | `Arc<RwLock<T>>`  |
| Async I/O-bound concurrency            | `tokio` / `async-std` (third-party) |

## Common mistakes to avoid

- Calling `.unwrap()` on `lock()` in production code — a panicked thread poisons the mutex; handle `PoisonError`.
- Holding a `MutexGuard` across an `.await` point in async code — use `tokio::sync::Mutex` instead.
- Spawning unbounded numbers of threads for I/O work — use a thread pool (`rayon` for CPU work, `tokio` for I/O).
