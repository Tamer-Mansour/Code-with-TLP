# Quiz - Concurrency and Parallelism

Test your understanding of Rust's concurrency primitives, the Send and Sync traits, and data-race prevention.

## Question 1

What compile-time error prevents you from sending an `Rc<T>` value to another thread?

- [ ] `Rc<T>` does not implement `Clone`
- [ ] `Rc<T>` does not implement `Debug`
- [x] `Rc<T>` does not implement `Send`, so it cannot be transferred to another thread
- [ ] `Rc<T>` panics at runtime if shared across threads

## Question 2

Which combination gives you shared, mutable state safely across multiple threads?

- [ ] `Rc<RefCell<T>>`
- [x] `Arc<Mutex<T>>`
- [ ] `Box<RefCell<T>>`
- [ ] `Arc<RefCell<T>>`

## Question 3

What is the difference between `Mutex<T>` and `RwLock<T>`?

- [ ] `Mutex` is for single-threaded use; `RwLock` is for multi-threaded use
- [x] `Mutex` allows only one reader or writer at a time; `RwLock` allows multiple concurrent readers but exclusive writers
- [ ] `RwLock` is always faster than `Mutex`
- [ ] `Mutex` operates on references; `RwLock` operates on owned values

## Question 4

What does `thread::spawn` require of the closure you pass it?

- [ ] The closure must implement `Fn`
- [ ] The closure must be `Clone`
- [x] The closure must be `Send + 'static` — it must be safe to send to another thread and contain no short-lived borrows
- [ ] The closure must implement `Copy`

## Question 5

What does the `mpsc` in `std::sync::mpsc` stand for?

- [ ] Multi-process, single-core
- [ ] Mutex-protected, single-consumer
- [x] Multi-producer, single-consumer
- [ ] Multi-purpose, safe concurrency

## Question 6

What happens if a thread panics while holding a `Mutex` lock?

- [ ] The lock is released normally and other threads continue
- [ ] The program aborts immediately
- [x] The mutex becomes **poisoned**: subsequent calls to `.lock()` return an `Err(PoisonError)` to signal that the data may be in an inconsistent state
- [ ] The lock is held forever, causing a deadlock

## Question 7

Does `Arc<Mutex<T>>` prevent **all** concurrency bugs?

- [ ] Yes — it prevents data races, deadlocks, and logic races
- [x] No — it prevents data races but not deadlocks, priority inversion, or application-level logic races
- [ ] Yes — Rust's type system guarantees all concurrent programs are correct
- [ ] No — `Arc<Mutex<T>>` is not thread-safe because `Mutex` can panic

## Question 8

What are **atomic types** (e.g., `AtomicUsize`) used for?

- [ ] Allocating memory on the heap atomically
- [ ] Thread-safe formatting and printing
- [x] Lock-free, thread-safe operations on single primitive values without the overhead of a mutex
- [ ] Ensuring that all threads finish before the program exits
