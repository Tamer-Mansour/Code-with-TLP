# Delta-Cycle Event Ordering Simulator

The SystemC scheduler processes events in a precise, deterministic order. Understanding that order is essential for predicting simulation behavior and debugging race conditions in your models.

## How the SystemC Scheduler Orders Work

When multiple processes are ready to run at the same simulation timestamp, the scheduler does not execute them simultaneously. Instead, it runs each ready process one at a time, collecting signal changes during the evaluate phase, then applying them all during the update phase. This pair — evaluate, then update — is one delta cycle.

Events scheduled with `sc_event::notify()` carry two ordering dimensions:

- **Timestamp**: the simulated time at which the event fires (e.g., 10 ns)
- **Delta offset**: events notified with `SC_ZERO_TIME` fire one delta cycle after the current one, at the same timestamp; immediately notified events fire in the current evaluate phase

## Key Distinction: Immediate vs SC_ZERO_TIME

A common misconception is that `SC_ZERO_TIME` is equivalent to an immediate notification because no real time advances. This is incorrect.

```cpp
// Fires in the CURRENT evaluate phase — other processes at this
// delta cycle may not yet have run
evt.notify();

// Fires at the START OF THE NEXT delta cycle — all processes
// in the current delta cycle complete first
evt.notify(SC_ZERO_TIME);
```

The IEEE 1666 standard is explicit: an immediately notified event activates processes during the current evaluate step, while an `SC_ZERO_TIME` notification schedules a new evaluate-update pair at the same timestamp. This controls the inter-process ordering within a single nanosecond boundary.

## Sorting Rules

When you reason about scheduler ordering, apply three keys in priority order:

1. **Timestamp** (ascending) — earlier time fires first
2. **Delta offset** (ascending) — lower delta index fires first at the same timestamp
3. **Process name** (alphabetical) — used as a tiebreaker when timestamp and delta are equal

The IEEE standard does not mandate alphabetical tiebreaking — actual simulators use unspecified ordering. However, for analysis exercises and interview questions, alphabetical order provides a deterministic, verifiable answer.

## Worked Example

Given these pending events:

```
Timestamp  Delta  Process
10         1      process_B
10         0      process_A
5          0      process_C
10         0      process_D
5          1      process_E
```

Sorting by (timestamp, delta, name):

| Timestamp | Delta | Process   |
|-----------|-------|-----------|
| 5         | 0     | process_C |
| 5         | 1     | process_E |
| 10        | 0     | process_A |
| 10        | 0     | process_D |
| 10        | 1     | process_B |

`process_A` and `process_D` share the same (10, 0) slot. In practice, the order between them is implementation-defined — alphabetical order gives a canonical answer for teaching purposes.

## Why This Matters for Correct Models

Models that depend on process execution order within a single delta cycle are fragile. The IEEE 1666 standard explicitly states that process execution order within one delta cycle is **unspecified**. Correct SystemC code must be written so that the final stable state is the same regardless of which ready process runs first.

If your model produces different results depending on process ordering, you have a design-level race condition. The fix is usually to add an extra delta cycle of separation using `SC_ZERO_TIME` notification, or to restructure the sensitivity lists.

## Reference

The normative rules for event notification and scheduler phases are defined in:

- **IEEE Std. 1666-2023** (available free via Accellera at https://www.accellera.org/downloads/standards/systemc): Sections 4.2 (simulation phases) and 5.10 (sc_event::notify semantics)
- **SystemC and TLM-2.0 Introductory Tutorial** (Doulos, free PDF at https://www.doulos.com/media/1408/systemc_tutorial.pdf): Chapters covering delta cycles and process scheduling

> **Interview answer:** The SystemC scheduler orders events first by timestamp, then by delta offset within a timestamp. Processes at the same timestamp and delta run in implementation-defined order — correct designs must not rely on that order.
