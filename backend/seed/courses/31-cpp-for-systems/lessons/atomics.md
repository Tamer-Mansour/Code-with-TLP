# std::atomic and Lock-Free Counters

Mutexes are correct but carry overhead: kernel involvement, context switches, and cache-line ping-pong. For simple shared variables — counters, flags, pointers — `std::atomic` provides **lock-free** (or at worst lock-based) operations that are guaranteed safe without a mutex.

## What Does Atomic Mean?

An operation is **atomic** if it appears instantaneous to all other threads — no thread can observe it in a half-finished state. The hardware provides atomic instructions such as `LOCK XADD` (x86) or `LDREX/STREX` (ARM).

## Basic Usage

```cpp
#include <atomic>
#include <iostream>
#include <thread>

std::atomic<int> counter{0};

void increment() {
    for (int i = 0; i < 100'000; ++i) {
        counter++;          // atomic read-modify-write
    }
}

int main() {
    std::thread t1(increment);
    std::thread t2(increment);
    t1.join(); t2.join();
    std::cout << counter.load() << '\n';  // always 200000
}
```

No mutex needed. `counter++` on an `std::atomic<int>` compiles to a single `LOCK XADD` instruction on x86.

## Key Operations

| Operation | Method | Description |
|---|---|---|
| Read | `load()` | Atomically read current value |
| Write | `store(v)` | Atomically write value |
| Read + write | `++`, `--`, `+=`, `-=` | Atomic increment/decrement |
| Swap | `exchange(v)` | Atomically replace, return old value |
| Conditional swap | `compare_exchange_weak/strong` | CAS operation |

```cpp
std::atomic<int> x{10};

int old = x.exchange(42);   // old = 10, x = 42

int expected = 42;
bool success = x.compare_exchange_strong(expected, 100);
// If x == expected (42), set x = 100 and return true
// Otherwise, load x into expected and return false
```

## Compare-And-Swap (CAS)

CAS is the foundation of lock-free data structures. It atomically performs:

```
if (x == expected) { x = desired; return true; }
else { expected = x; return false; }
```

`compare_exchange_weak` may spuriously fail (returns false even when x == expected) — use it in a loop for better performance on some architectures. `compare_exchange_strong` never spuriously fails.

```cpp
// Lock-free push to a stack (simplified)
std::atomic<Node*> head{nullptr};

void push(Node* node) {
    node->next = head.load();
    while (!head.compare_exchange_weak(node->next, node)) {
        // head changed, retry — node->next was updated automatically
    }
}
```

## std::atomic<bool>: Flags

```cpp
std::atomic<bool> stop_flag{false};

void worker() {
    while (!stop_flag.load()) {
        // do work
    }
}

// From another thread:
stop_flag.store(true);
```

Without `std::atomic`, reading `stop_flag` in the worker loop is a data race — the compiler may cache the value in a register and never re-read memory.

## std::atomic<T*>: Atomic Pointers

Useful for publish-subscribe patterns:

```cpp
std::atomic<Config*> current_config{nullptr};

// Publisher thread
Config* cfg = new Config{...};
current_config.store(cfg, std::memory_order_release);

// Consumer threads — read safely
Config* cfg = current_config.load(std::memory_order_acquire);
if (cfg) { use(*cfg); }
```

## What Types Can Be Atomic?

`std::atomic<T>` requires `T` to be trivially copyable. In practice:

- `bool`, integral types, pointers: guaranteed lock-free on most platforms.
- Larger types (structs): may fall back to an internal mutex — check `is_lock_free()`.

```cpp
std::atomic<int> a;
std::cout << a.is_lock_free() << '\n';  // 1 on most platforms
```

## Atomic vs Mutex: When to Use Each

| Use `std::atomic` | Use `std::mutex` |
|---|---|
| Single integer/bool/pointer | Multiple related variables |
| Counters, flags, statistics | Complex invariants spanning fields |
| Lock-free algorithms | Protecting a data structure |
| High-contention hot path | Rarely contested critical section |

> **Interview answer:** `std::atomic<T>` makes reads and writes to a variable indivisible — no torn reads, no lost updates. For simple counters and flags it avoids mutex overhead entirely. Under the hood it uses hardware atomic instructions (like `LOCK XADD` on x86). For multiple related variables that must change together, a mutex is still required.
