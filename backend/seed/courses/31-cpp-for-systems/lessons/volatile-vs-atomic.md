# volatile vs atomic: A Common Confusion

`volatile` and `std::atomic` address different problems. Confusing them is one of the most common mistakes in systems programming interviews.

## What Each One Prevents

| Concern | `volatile` | `std::atomic` |
|---|---|---|
| Compiler eliding/caching reads | Yes | Yes (side effect of atomics) |
| Compiler reordering accesses | Partial (within volatile accesses) | Yes, with memory_order |
| CPU out-of-order execution | No | Yes (default: seq_cst) |
| Torn reads/writes (non-atomicity) | No | Yes |
| Data races between threads | No | Yes |

## volatile Is Not Enough for Threads

Consider a flag shared between two CPU cores:

```cpp
// WRONG: volatile does not prevent CPU reordering or torn writes
volatile bool ready = false;
volatile int  data  = 0;

// Thread A:
data  = 42;
ready = true;   // CPU B may observe ready=true but data still 0 due to store reorder

// Thread B:
while (!ready) {}
assert(data == 42);  // may FAIL
```

The compiler will not reorder these two writes. But the **CPU's store buffer** may deliver them to other cores out of order. `volatile` does not emit any memory fence instruction.

## std::atomic Provides the Full Package

```cpp
#include <atomic>
std::atomic<bool> ready{false};
std::atomic<int>  data{0};

// Thread A:
data.store(42, std::memory_order_relaxed);
ready.store(true, std::memory_order_release);  // release fence: all prior stores visible

// Thread B:
while (!ready.load(std::memory_order_acquire)) {}  // acquire fence
assert(data.load(std::memory_order_relaxed) == 42);  // always passes
```

The `release`/`acquire` pair establishes a **happens-before** relationship across threads — the C++ memory model's formal guarantee.

## When volatile Is Still Correct

`volatile` is the right tool when the "other writer" is **hardware**, not another thread:

```cpp
// Hardware timer register — no other CPU thread, just the hardware incrementing it
volatile uint32_t* TIMER_COUNT = (volatile uint32_t*)0x4000'2000;
uint32_t now = *TIMER_COUNT;  // must read fresh from bus every time
```

Here no CPU memory fence is needed; the issue is purely compiler optimization. `std::atomic` would work too, but it imposes unnecessary fence overhead and is semantically misleading for MMIO.

## The Dual Use Myth

Some embedded code uses `volatile` for ISR-shared variables and assumes it is sufficient. Whether it is safe depends on:

1. **Single-core vs multi-core.** On a single-core bare-metal MCU, disabling interrupts around critical sections is sufficient; `volatile` just prevents the compiler optimization issue.
2. **ISR on the same core.** An ISR runs on the same core that interrupted main. The CPU cannot "reorder" an interrupt — the ISR executes to completion before returning. So `volatile` is adequate.
3. **Multi-core SMP.** Both ISR-shared and thread-shared data need proper synchronization — `std::atomic` or explicit barriers.

## Quick Decision Table

| Scenario | Use |
|---|---|
| MMIO hardware register | `volatile` |
| Flag set by ISR, read by main (single-core) | `volatile` |
| Shared counter between two threads | `std::atomic` |
| Shared flag (producer/consumer, multi-core) | `std::atomic` with release/acquire |
| Both MMIO and shared with threads | `volatile std::atomic` (rare, platform-specific) |

## Example: The Lock-Free Ring Buffer Flag

```cpp
#include <atomic>

struct RingBuffer {
    char   data[256];
    std::atomic<int> head{0};
    std::atomic<int> tail{0};
};
```

Using `std::atomic<int>` on `head` and `tail` allows one producer and one consumer thread to share the ring buffer without a mutex, with correct visibility guarantees.

> **Interview answer:** "`volatile` only prevents compiler optimizations — it does not prevent CPU reordering or guarantee atomicity. For multi-threaded shared data you need `std::atomic`, which provides both atomicity and memory ordering. `volatile` is correct for hardware registers and single-core ISR flags."
