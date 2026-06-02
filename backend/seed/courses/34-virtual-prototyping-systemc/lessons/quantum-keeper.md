# The Quantum Keeper and Local Time

The **quantum keeper** (`tlm_utils::tlm_quantumkeeper`) is a utility class in the TLM-2.0 reference implementation that automates the bookkeeping of temporal decoupling. Instead of manually managing a local `sc_time` variable and calling `wait()` at the right moment, the quantum keeper handles it for you.

## The Problem It Solves

Manual temporal decoupling (from the previous lesson) requires the initiator to:
1. Keep a `sc_time local_time` variable.
2. Add annotated delays after each `b_transport`.
3. Periodically compare local_time to the quantum.
4. Call `wait(local_time)` and reset local_time to zero.

This is error-prone. Forgetting the reset or the comparison introduces subtle timing bugs. The quantum keeper encapsulates all of this.

## Quantum Keeper API

```cpp
#include "tlm_utils/tlm_quantumkeeper.h"

// --- Module setup ---
tlm_utils::tlm_quantumkeeper m_qk;

void start_of_simulation() override {
    // Set the global quantum — shared across all initiators
    tlm_utils::tlm_quantumkeeper::set_global_quantum(
        sc_core::sc_time(1, SC_US));   // 1 µs quantum

    // Reset the keeper's local time to global time
    m_qk.reset();
}
```

```cpp
// --- In the initiator thread ---
void cpu_thread() {
    while (true) {
        tlm::tlm_generic_payload trans;
        sc_core::sc_time delay = m_qk.get_local_time();
        // delay is RELATIVE to sc_time_stamp(); target adds to it

        socket->b_transport(trans, delay);

        // Tell the keeper about the new local time
        m_qk.set(delay);

        // Keeper automatically calls wait() if quantum exceeded
        if (m_qk.need_sync()) {
            m_qk.sync();   // waits and resets local time
        }
    }
}
```

## Local Time vs. Global Time — The Keeper's View

```
Global time:  ─────────────┬─────────────────────────────────────────►
                            │ sc_time_stamp() = 5 µs
                            │
Local time offset: +300 ns  +600 ns  +1100 ns (>1 µs quantum)
                    ───────────────────────────────────────────────────►
                         ↑                ↑
                   need_sync()=false   need_sync()=true → sync() called
                                       Global time advances to 6.1 µs
```

## Key Methods

| Method | Description |
|---|---|
| `set_global_quantum(t)` | Sets the quantum for all keepers (static) |
| `get_global_quantum()` | Returns the current global quantum |
| `reset()` | Syncs keeper to current `sc_time_stamp()` |
| `get_local_time()` | Returns current local time offset |
| `set(t)` | Updates local time after a b_transport call |
| `need_sync()` | True if local time >= global quantum |
| `sync()` | Calls `wait(local_time)` and resets |
| `inc(t)` | Increments local time by `t` (no sync check) |

## The Global Quantum

The quantum keeper uses a **single global quantum** shared across all initiator instances. This is intentional: if CPU0 has a 500 ns quantum and CPU1 has a 2 µs quantum, CPU1 can observe CPU0's writes up to 1.5 µs late. A uniform global quantum bounds the maximum observation skew across all initiators.

```cpp
// Recommended: set in sc_main before simulation starts
tlm_utils::tlm_quantumkeeper::set_global_quantum(
    sc_core::sc_time(10, SC_US));
```

## Worked Example: Four Memory Accesses

Assume global quantum = 1 µs, each access annotates 300 ns.

```
Start: global_time = 0, local_time = 0

Access 1: b_transport annotates 300 ns → set(300 ns), need_sync() = false
Access 2: b_transport annotates 300 ns → set(600 ns), need_sync() = false
Access 3: b_transport annotates 300 ns → set(900 ns), need_sync() = false
Access 4: b_transport annotates 300 ns → set(1200 ns), need_sync() = TRUE
  → sync(): wait(1200 ns), global_time advances to 1200 ns, local_time = 0

Total scheduler calls: 1 wait() for 4 transactions (instead of 4)
```

## Common Pitfalls

- **Forgetting `m_qk.reset()` at start_of_simulation** — the keeper's internal state is undefined until reset.
- **Passing `m_qk.get_local_time()` to b_transport and then calling `m_qk.set(delay)`** — the delay passed to b_transport is an inout parameter; the target adds to it. After the call, `delay` holds the updated value; pass that to `set()`.
- **Using different quantum values in different modules** — only the global quantum matters; per-keeper custom values are not supported in standard tlm_quantumkeeper.

> **Interview answer:** "The quantum keeper automates temporal decoupling: it tracks the local time offset, compares it against the global quantum after each transaction, and calls `wait()` only when synchronization is needed — one wait per quantum period instead of one per transaction."
