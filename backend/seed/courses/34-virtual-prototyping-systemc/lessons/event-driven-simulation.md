# Event-Driven Simulation Explained

Event-driven simulation is the foundational execution model behind SystemC. Instead of advancing time in fixed steps and recalculating the entire system state on every tick, the simulator jumps forward only when something meaningful happens — an **event**. This makes it orders of magnitude faster for hardware models where most signals are idle most of the time.

## What Is an Event?

An event is a notification that something has changed or a condition has been met. In SystemC, events are represented by `sc_event` objects. A process can:

- **Wait** for an event (suspend itself)
- **Notify** an event (wake up waiting processes)

```cpp
sc_event my_event;

// In one thread: wait for the event
void consumer() {
    while (true) {
        wait(my_event);          // suspend until notified
        std::cout << "Event fired at " << sc_time_stamp() << "\n";
    }
}

// In another thread: trigger the event
void producer() {
    wait(10, SC_NS);
    my_event.notify();           // immediate notification
}
```

## Why Not a Clock-Driven Loop?

A naive simulator could tick every nanosecond and ask "did anything change?" This is simple but wasteful. A 10-microsecond simulation with 1 ns resolution requires 10,000 iterations even if only 5 events occur. Event-driven simulation skips straight to those 5 points in time.

| Approach | Iterations for 10 µs idle | CPU time |
|---|---|---|
| Fixed-tick (1 ns) | 10,000 | High |
| Event-driven (5 events) | 5 | Minimal |

## The Event Queue

The SystemC kernel maintains a **global event queue** — an ordered list of (time, event) pairs. When a process notifies an event with a time delay, that notification is inserted into the queue. The kernel always pops the earliest entry and advances simulation time to that point.

```
Event Queue (sorted by time):
  [10 ns]  → data_ready
  [25 ns]  → bus_grant
  [25 ns]  → irq_line
  [100 ns] → timeout
```

Multiple events can share the same timestamp (they are processed in the same **simulation step**, potentially across multiple **delta cycles** — more on that in later lessons).

## Types of Event Notification

SystemC provides three notification modes:

- **Immediate** (`notify()`): fires right now, within the current evaluation phase. Processes sensitive to this event are activated in the same delta cycle.
- **Delta** (`notify(SC_ZERO_TIME)`): fires at the same simulation time but in the *next* delta cycle, allowing signal updates to propagate.
- **Timed** (`notify(10, SC_NS)`): fires at a future simulation time.

```cpp
my_event.notify();               // immediate
my_event.notify(SC_ZERO_TIME);   // next delta
my_event.notify(10, SC_NS);      // 10 ns from now
```

## Sensitivity Lists

Processes declare what they are sensitive to using sensitivity lists. The kernel only runs a process when one of its trigger conditions is satisfied.

```cpp
SC_METHOD(my_process);
sensitive << clk.pos() << reset;   // runs on rising clock or reset change
```

## Common Pitfalls

- **Infinite zero-time loops**: if two processes keep notifying each other with `SC_ZERO_TIME`, simulation time never advances. SystemC will spin indefinitely. Always ensure at least one timed wait breaks the cycle.
- **Lost notifications**: immediate notifications sent before any process has called `wait()` are lost — use delta or timed notifications when ordering is uncertain.
- **Event vs. signal**: `sc_signal` drives its update logic through the delta-cycle mechanism; `sc_event` is lower-level and fires once per notification.

## Interview Answer

> "Event-driven simulation advances time only to the next scheduled event rather than ticking every time unit. The kernel maintains a sorted event queue, pops the earliest entry, advances simulation time, and runs all processes sensitive to that event — making simulation fast even over long time spans."
