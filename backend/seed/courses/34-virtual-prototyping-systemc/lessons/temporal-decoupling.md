# Temporal Decoupling

**Temporal decoupling** is the technique that makes LT virtual prototypes fast enough to boot embedded operating systems. Instead of synchronizing every transaction with the SystemC scheduler, an initiator runs ahead of global simulation time, accumulating a *local time offset*, and only synchronizes when that offset exceeds a configured limit called the **time quantum**.

## The Problem Without Temporal Decoupling

Without temporal decoupling, every memory access requires:
1. The initiator calls `b_transport`.
2. The target annotates a delay (e.g., 10 ns).
3. The initiator calls `wait(10 ns)`.
4. The SystemC scheduler advances time and resumes the thread.

On a 500 MHz processor model doing 500 million memory accesses per simulated second, this is 500 million scheduler context switches per simulated second. That is catastrophically slow.

## The Solution: Run Ahead, Sync Later

With temporal decoupling, the initiator keeps a local `sc_time` variable (its **local time**). Instead of calling `wait()` after each transaction, it adds the annotated delay to its local time. Only when local time exceeds `quantum` does it call `wait(local_time - sc_time_stamp())` to sync.

```cpp
// Temporal decoupling pattern — manual implementation
void cpu_thread() {
    sc_core::sc_time local_time = sc_core::SC_ZERO_TIME;
    const sc_core::sc_time QUANTUM(1000, SC_NS);   // 1 µs quantum

    for (int i = 0; i < NUM_ACCESSES; ++i) {
        tlm::tlm_generic_payload trans;
        setup_trans(trans, addr[i], data[i]);

        // b_transport annotates delay INTO local_time
        socket->b_transport(trans, local_time);

        // Check quantum — sync only when needed
        if (local_time >= QUANTUM) {
            wait(local_time);                // advance global time once
            local_time = sc_core::SC_ZERO_TIME;
        }
    }
}
```

## Scheduler Context Switches: Before vs. After

```
Without temporal decoupling (1000 transactions, 10 ns each):
  1000 wait() calls → 1000 scheduler context switches → 10 µs simulated

With temporal decoupling (quantum = 1 µs = 100 transactions):
  10 wait() calls → 10 scheduler context switches → 10 µs simulated
  Speedup: 100x on scheduler alone
```

## Global vs. Local Time

| Concept | Variable | Updated by |
|---|---|---|
| Global simulation time | `sc_time_stamp()` | Scheduler (`wait()`) |
| Local time (offset) | `sc_time local_time` | b_transport annotation |
| Effective time | `sc_time_stamp() + local_time` | Computed by initiator |

The initiator's **effective time** is always equal to or ahead of global simulation time. This is the "decoupling" — the initiator is temporally ahead by up to one quantum.

## Correctness Constraints

Temporal decoupling is correct **as long as:**

- No thread observes the initiator's transactions before the next sync point. (Other threads see global time, not local time.)
- The initiator does not sample global signals (e.g., interrupt lines) with a stale clock. If an interrupt could arrive between two transactions in the same quantum, the software could miss it by up to one quantum period.
- The quantum is chosen small enough that the missed interrupt window is acceptable.

## Choosing the Quantum

Larger quantum = faster simulation but worse timing accuracy. Common choices:

| Quantum | Use Case |
|---|---|
| 100 ns | Tight real-time systems (quantum smaller than ISR latency) |
| 1 µs | General embedded software |
| 10 µs | OS boot benchmarking (speed priority) |
| 1 ms | Very loose exploration models |

A quantum of 1 µs on a 500 MHz processor means the CPU runs ~500 instructions per sync. This is a good default for most embedded Linux bring-up scenarios.

## Common Pitfalls

- **Resetting local_time to zero after `wait()`** — forgetting this leaves the initiator perpetually ahead by one quantum.
- **Using the quantum keeper** (covered in the next lesson) eliminates this manual bookkeeping.
- **Calling `wait()` inside a target's `b_transport`** breaks temporal decoupling by forcing the scheduler to intervene on every call.

> **Interview answer:** "Temporal decoupling lets an initiator accumulate annotated delays in a local time variable and sync with the scheduler only once per quantum period. This reduces context switches from one per transaction to one per quantum, dramatically accelerating simulation."
