# Loosely-Timed vs Approximately-Timed Latency

TLM-2.0 defines two standard coding styles for timing accuracy: Loosely-Timed (LT) and Approximately-Timed (AT). Understanding the tradeoff between them is essential for selecting the right model for each phase of an SoC project.

## Loosely-Timed (LT) Style

In the LT style, the initiator uses **temporal decoupling**. Rather than synchronizing with the global simulation clock after every transaction, the initiator accumulates a local time offset. Only when this offset reaches or exceeds the **quantum** does the process synchronize — calling `tlm_quantum_keeper::sync()` to advance the global clock.

```cpp
// LT initiator fragment
sc_core::sc_time local_time = sc_core::SC_ZERO_TIME;
const sc_core::sc_time QUANTUM(1000, sc_core::SC_NS);

for (int i = 0; i < NUM_TRANSACTIONS; ++i) {
    // annotate a per-transaction delay
    local_time += sc_core::sc_time(10, sc_core::SC_NS);

    if (local_time >= QUANTUM) {
        wait(local_time);      // sync: advance global clock
        local_time = SC_ZERO_TIME;
    }
    socket->b_transport(trans, local_time);
}
```

The benefit is that the simulation kernel performs far fewer context switches. An initiator running 1000 transactions with a 1000 ns quantum and 10 ns per transaction only synchronizes once per 100 transactions — reducing scheduler overhead by 100x compared to synchronizing after every call.

## Approximately-Timed (AT) Style

In the AT style, every transaction phase is individually timed. A four-phase bus protocol models `BEGIN_REQ`, `END_REQ`, `BEGIN_RESP`, and `END_RESP` as separate events, each with a real time annotation.

```
BEGIN_REQ  ────►  (bus latency phase 1)
END_REQ    ────►  (bus latency phase 2)
BEGIN_RESP ◄────  (bus latency phase 3)
END_RESP   ◄────  (bus latency phase 4)
```

This models bus pipelining — a second request can start before the first response completes. The result is accurate microarchitectural behavior at the cost of more simulation events and thus lower simulation speed.

## LT vs AT: Use Case Guidance

| Use Case | Recommended Style |
|----------|------------------|
| Early software bring-up | LT |
| OS boot and driver development | LT |
| Functional verification of software | LT |
| Bus bandwidth and latency analysis | AT |
| Cache miss modeling | AT |
| Pipeline contention studies | AT |

A common misconception is that AT is always "better" than LT. This is wrong: LT can boot an embedded Linux in minutes; the equivalent AT model might take hours. For software work, LT is the correct choice.

## Computing LT Total Time

The LT total simulated time depends on quantum alignment:

```
LT_total = ceil(T * bus_latency / quantum) * quantum
```

If 100 transactions each take 10 ns and the quantum is 50 ns, then `T * bus_latency = 1000 ns`. `ceil(1000 / 50) * 50 = 1000 ns`. Alignment to the quantum means the final sync point is rounded up to the nearest multiple.

## Computing AT Total Time

AT is straightforward: every transaction contributes its full latency with no batching.

```
AT_total = T * bus_latency
```

## Speedup Factor

The simulation speedup of LT over AT is:

```
speedup = AT_total / LT_total
```

When the quantum evenly divides the total workload, LT and AT totals are equal and speedup is 1.0. In practice, LT simulations run 10–100x faster because fewer global synchronization points means fewer scheduler wakeups.

## Reference

For the normative definitions of LT and AT coding styles:

- **OSCI TLM-2.0 Language Reference Manual** (free PDF from Accellera at https://www.accellera.org/images/downloads/standards/systemc/TLM_2_0_LRM.pdf): Sections 9 and 10 cover LT and AT coding styles in full
- **TLM-2.0 Tutorial Series** (Doulos KnowHow at https://www.doulos.com/knowhow/systemc/tlm-20/): Tutorial 4 covers non-blocking transport and temporal decoupling with quantum keeper examples

> **Interview answer:** LT uses temporal decoupling — an initiator accumulates a local time offset and only syncs when it exceeds the quantum, minimizing context switches. AT models each bus phase separately for accurate pipeline behavior. LT is used for fast software bring-up; AT is used for microarchitectural analysis. Neither is universally superior.
