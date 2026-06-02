# std::thread: Launching, Joining, and Detaching

`std::thread`, introduced in C++11, gives portable access to OS threads without touching `pthreads` or Win32 API directly. It wraps a callable — a function, lambda, or function object — and launches it immediately on construction.

## Launching a Thread

```cpp
#include <iostream>
#include <thread>

void greet(const std::string& name) {
    std::cout << "Hello from thread, " << name << '\n';
}

int main() {
    std::thread t(greet, "Alice");  // thread starts immediately
    t.join();                        // main waits for t to finish
}
```

Arguments are **forwarded** to the callable. For references, wrap with `std::ref()` — raw reference arguments are copied by default to avoid dangling references.

```cpp
void increment(int& value) { value++; }

int x = 0;
std::thread t(increment, std::ref(x));  // must use std::ref
t.join();
// x is now 1
```

## Joining a Thread

`join()` blocks the calling thread until the target thread completes. After `join()`, the `std::thread` object no longer represents a running thread and its destructor is safe.

**Rule:** Every joinable thread must be either joined or detached before its destructor runs. If the destructor runs on a joinable thread, `std::terminate()` is called — the program crashes.

```cpp
std::thread t(some_task);
// ... do other work ...
t.join();  // MUST call this (or detach) before t goes out of scope
```

## Detaching a Thread

`detach()` releases ownership of the thread. The OS cleans it up when it finishes. The `std::thread` object becomes non-joinable immediately.

```cpp
std::thread t(background_logger);
t.detach();  // fire and forget — we no longer track it
```

**Pitfall:** A detached thread must not access objects that may be destroyed before it finishes. A common bug is detaching a thread that captures a local variable by reference, then returning from the function.

```cpp
// DANGER: local string may be destroyed before thread uses it
void bad() {
    std::string msg = "hello";
    std::thread t([&msg]() {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        std::cout << msg;  // msg is gone!
    });
    t.detach();
}  // msg destroyed here
```

## Checking Joinability

```cpp
std::thread t;          // default-constructed: not joinable
if (t.joinable()) {
    t.join();
}
```

## RAII Wrapper: jthread (C++20)

C++20 introduced `std::jthread`, which automatically joins in its destructor and supports cooperative cancellation via `std::stop_token`.

```cpp
#include <thread>

void worker(std::stop_token st) {
    while (!st.stop_requested()) {
        // do work
    }
}

int main() {
    std::jthread t(worker);
    // t.join() called automatically at end of scope
}
```

## Hardware Concurrency

```cpp
unsigned int cores = std::thread::hardware_concurrency();
// Returns number of logical CPU cores (0 if unknown)
```

## Thread Identity

Each thread has a unique ID accessible via `std::this_thread::get_id()`.

```cpp
std::cout << "Running on thread " << std::this_thread::get_id() << '\n';
```

## Common Patterns

| Goal | Mechanism |
|---|---|
| Parallelize N tasks | Launch N threads, store in `std::vector<std::thread>`, join all |
| Background logging | Detach one logger thread |
| Cancel long task | Use `std::jthread` + `stop_token` |
| Pass result back | Use `std::future` / `std::promise` (covered later) |

```cpp
// Parallel worker pool pattern
std::vector<std::thread> workers;
for (int i = 0; i < 4; ++i) {
    workers.emplace_back([i]() {
        do_work(i);
    });
}
for (auto& w : workers) {
    w.join();  // wait for all
}
```

> **Interview answer:** `std::thread` launches a callable immediately on construction. You must call `join()` (to wait) or `detach()` (to release ownership) before the object is destroyed, or the program calls `std::terminate()`. Use `std::jthread` in C++20 for automatic joining.
