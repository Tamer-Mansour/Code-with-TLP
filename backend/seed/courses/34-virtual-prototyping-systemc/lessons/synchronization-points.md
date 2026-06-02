# Synchronization Between HW and SW Domains

When software runs at potentially thousands of MIPS inside an ISS while hardware models advance their own clocks through the SystemC scheduler, the two must periodically reconcile their view of simulated time. This reconciliation — synchronization — is the mechanism that keeps co-simulation causally consistent.

## Why Synchronization Is Needed

Temporal decoupling lets the ISS run ahead of the SystemC clock (accumulating time locally) to avoid calling `wait()` on every instruction. But an ISS that has run 10 000 instructions into the future cannot yet respond to an interrupt that the hardware model will raise in 5 000 simulated cycles — the interrupt is in the ISS's past relative to the current SystemC time.

Without synchronization:
- SW may miss time-sensitive interrupts.
- HW event ordering becomes non-deterministic.
- Race conditions between DMA completion and CPU access appear in simulation but not in hardware (or vice-versa).

## Synchronization Primitives

### `sc_time` and `wait()`

`wait(delay)` is the fundamental synchronization call. When the ISS calls it, control returns to the SystemC scheduler, which can advance other processes and deliver events.

```cpp
void Iss::execute_quantum() {
    for (int i = 0; i < QUANTUM_INSTRUCTIONS; i++) {
        execute_one();
        local_time += CYCLE_TIME;
    }
    wait(local_time);      // give up control, sync with rest of platform
    local_time = SC_ZERO_TIME;
}
```

### `tlm_quantumkeeper`

`tlm_quantumkeeper` manages the local time budget automatically:

```cpp
#include "tlm_utils/tlm_quantumkeeper.h"

tlm_utils::tlm_quantumkeeper qk;
// Set global quantum (shared across all LT initiators)
qk.set_global_quantum(sc_time(1, SC_US)); // 1 µs

void Iss::run_loop() {
    while (true) {
        execute_one_instruction();
        qk.inc(sc_time(1, SC_NS)); // account for one clock cycle
        if (qk.need_sync()) {
            qk.sync();             // calls wait() when quantum expires
        }
    }
}
```

The global quantum is shared across all LT models. The smallest quantum in the system sets the effective synchronization granularity.

## Interrupt Synchronization

Interrupts cross the HW→SW boundary via `sc_signal<bool>`. The signal write by a peripheral creates a delta-cycle notification, which the scheduler delivers at the next `wait()` in the ISS:

```
Peripheral model               SystemC kernel            ISS
      |                             |                     |
      |-- irq_line.write(true) ---> |                     |
      |                             | [delta cycle]       |
      |                             | notify ISS process  |
      |                             |-------------------> |
      |                             |                     | check_irq()
      |                             |                     | push context
      |                             |                     | jump ISR
```

The ISS must poll or `wait_until` on the IRQ signal at each quantum boundary.

## Event-Driven Synchronization

For fine-grained synchronization, `sc_event` and `wait(event)` suspend the ISS until a specific hardware event fires:

```cpp
// ISS waits for DMA to finish before reading result buffer
void Cpu::do_dma_and_wait() {
    start_dma(src, dst, len);      // trigger DMA hardware model
    wait(dma_done_event);          // suspend ISS until DMA fires event
    process_result(dst);           // guaranteed: DMA complete
}
```

This is more precise than polling but requires the peripheral to expose the `sc_event`.

## The Synchronization Granularity Problem

| Quantum | ISS efficiency | IRQ latency accuracy |
|---|---|---|
| 1 ns | Very low (sync every cycle) | Exact |
| 100 ns | Low | ±100 ns |
| 1 µs | Good | ±1 µs |
| 10 µs | High | ±10 µs |
| 1 ms | Very high | May miss fast IRQs |

For most embedded applications, 1–10 µs quantums balance speed and fidelity.

## Worked Example: Tight Synchronization for a Real-Time Task

```cpp
// RTOS tick ISR fires every 1 ms — quantum must be ≤ 1 ms
qk.set_global_quantum(sc_time(500, SC_US)); // 500 µs: two syncs per tick

// Timer peripheral raises IRQ every 1 ms of simulated time
void SysTickModel::tick_process() {
    while (true) {
        wait(sc_time(1, SC_MS));
        irq_out.write(true);
        wait(SC_ZERO_TIME);      // delta: let ISS see the signal
        irq_out.write(false);
    }
}
```

With a 500 µs quantum, the ISS checks for the tick interrupt within 500 µs of it firing — acceptable for a 1 ms tick.

## Common Pitfalls

- **Forgetting `wait(SC_ZERO_TIME)` after signal write** — Without a delta-cycle advance, the ISS may not observe the new signal value until the next full quantum.
- **Over-synchronization** — Using a 1 ns quantum for a peripheral that only fires IRQs every millisecond wastes simulation speed for no accuracy gain.
- **Re-entrancy in `b_transport`** — A peripheral that calls `wait()` inside `b_transport` can cause TLM protocol violations if called from an LT initiator expecting a non-blocking return.

## Interview Answer

> "HW and SW are synchronized via `wait()` calls in the ISS's `SC_THREAD`. The `tlm_quantumkeeper` lets the ISS run a configurable quantum of instructions before yielding control to the SystemC scheduler. Interrupts cross the boundary via `sc_signal<bool>`; DMA completion can use `sc_event`. The quantum size determines the tradeoff between simulation speed and interrupt timing accuracy."
