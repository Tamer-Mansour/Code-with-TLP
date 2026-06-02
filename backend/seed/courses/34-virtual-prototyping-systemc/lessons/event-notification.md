# Immediate, Delta, and Timed Notification

`sc_event::notify()` has three distinct scheduling modes that control *when* waiting processes are awakened. Choosing the wrong mode is one of the most common sources of subtle simulation bugs in SystemC.

## The SystemC Simulation Loop

To understand notification, you must understand the simulation loop structure:

```
while (events_pending) {
    advance_time_to_next_event();          // time step
    do {
        run_all_ready_processes();         // evaluation phase
        update_all_channels();             // update phase (delta-cycle writes)
        delta++;
    } while (processes_became_ready);     // repeat until stable
}
```

One "time step" can contain many *delta cycles* — zero-time iterations that propagate signal changes. Notification mode determines which phase a process enters when woken.

## Mode 1: Immediate Notification

```cpp
event.notify();   // no argument = immediate
```

Processes waiting on this event are made **runnable immediately**, in the current evaluation phase. They execute before the current set of processes finishes.

**Key rule**: immediate notification cannot target the future — it fires now or never. If called inside an `SC_METHOD`, it causes all sensitive processes (including potentially the caller itself) to be re-scheduled in the same delta, risking infinite loops.

```cpp
// DANGER: can cause infinite loop
SC_METHOD(bad_method);
sensitive << my_event;

void bad_method() {
    my_event.notify();   // immediate: this method will re-run immediately
}
```

**Use when**: signaling a pure synchronization point with no time passing (e.g., a channel notifying its value-changed event).

## Mode 2: Delta-Cycle Notification

```cpp
event.notify(SC_ZERO_TIME);
```

The notification is delivered at the **start of the next delta cycle** — zero simulated time advances, but the current evaluation phase completes first, and all pending channel updates happen before the woken processes run.

```cpp
SC_MODULE(Safe) {
    sc_event handoff;

    SC_CTOR(Safe) {
        SC_THREAD(sender);
        SC_THREAD(receiver);
    }

    void sender() {
        wait(5, SC_NS);
        handoff.notify(SC_ZERO_TIME);   // receiver wakes next delta
    }

    void receiver() {
        wait(handoff);
        std::cout << "Received at " << sc_time_stamp() << "\n"; // 5 ns
    }
};
```

**Use when**: you need to pass a notification within the same simulated time step but want to avoid re-entrancy issues from immediate notify.

## Mode 3: Timed Notification

```cpp
event.notify(10, SC_NS);    // after 10 nanoseconds
event.notify(1, SC_US);     // after 1 microsecond
event.notify(sc_time(500, SC_PS));  // after 500 picoseconds
```

The notification is scheduled in the future event queue. Simulation time advances to the notification time before the waiting processes are awakened.

```cpp
void timer_thread() {
    timeout_event.notify(100, SC_NS);   // schedule 100 ns from now
    wait(timeout_event);                // will wake at T+100ns
    handle_timeout();
}
```

**Use when**: modeling real hardware delays, clock generators, timeouts, and anything where simulated time must pass.

## Cancellation Rules

When `notify()` is called multiple times for the same event before it fires, the rules are:

| Existing pending | New call | Result |
|---|---|---|
| Timed (T+10) | `notify(T+5)` | Earlier time wins; T+10 is cancelled |
| Timed (T+5) | `notify(T+10)` | Earlier time wins; T+10 is ignored |
| Timed (T+10) | `notify()` immediate | Immediate fires now; timed is cancelled |
| Delta | `notify()` immediate | Immediate fires now; delta is cancelled |

Only one pending notification per event exists at any time. Use `sc_event_queue` to queue multiple timed notifications.

## Comparison Table

| Mode | Simulated Time Advance | When Process Wakes |
|---|---|---|
| `notify()` | None | Current evaluation phase |
| `notify(SC_ZERO_TIME)` | None (next delta) | Next evaluation phase |
| `notify(T, SC_NS)` | T nanoseconds | After T ns |

## Worked Example: Clock Generator

```cpp
SC_MODULE(ClockGen) {
    sc_out<bool> clk;
    sc_event     toggle_event;

    SC_CTOR(ClockGen) {
        SC_THREAD(generate);
        clk.initialize(false);
    }

    void generate() {
        while (true) {
            clk.write(!clk.read());         // toggle
            toggle_event.notify(5, SC_NS);  // timed: next toggle in 5ns
            wait(toggle_event);             // suspend until then
        }
    }
};
```

This produces a 10 ns period (100 MHz) clock using timed notification — the most common pattern for driving clocks in SystemC testbenches.

> **Interview answer:** SystemC `sc_event` supports three notification modes: immediate (current delta, highest priority), delta-cycle (`SC_ZERO_TIME`, next delta), and timed (future simulation time); each subsequent pending notification cancels the previous one for the same event, so only one notification is ever outstanding.
