# Kernel Scheduler Phases

The SystemC kernel scheduler orchestrates simulation execution through a well-defined sequence of phases. Knowing this sequence lets you predict exactly when processes run, when events fire, and when simulation time advances — critical for debugging complex models.

## The Seven Scheduler Phases

The IEEE 1666-2011 standard defines the following phases:

### 1. Initialization Phase

Runs once at the start of `sc_start()`. Every `SC_METHOD` and `SC_THREAD` process is run once (or started), even if no event has triggered it. This populates initial signal values and advances all threads to their first `wait()`.

```cpp
// This SC_METHOD will run once during initialization
void my_method() {
    output.write(input.read() ^ mask);
}
```

### 2. Evaluate Phase

All runnable processes execute. A process becomes runnable when:
- An event it is sensitive to is notified (immediate or delta notification)
- It was awakened from a timed wait

Processes run to their next suspension point (`wait()` for threads, end-of-function for methods).

### 3. Update Phase

Pending signal writes are committed. Signal objects check whether their new value differs from the old. If so, a **delta notification** is generated for that signal's event.

### 4. Delta Notification Phase

Events created during the update phase (from signal value changes) are delivered. Processes sensitive to these events become runnable, setting up the next evaluate phase.

Steps 2–4 repeat (as delta cycles) until no new events are pending at the current time.

### 5. Timed Notification Phase

Once quiescence is reached at the current time, the kernel scans the timed event queue and delivers all events scheduled for the next time point. Simulation time advances.

### 6. Ready to Run

Processes that were waiting on timed events are made runnable. Control returns to the evaluate phase.

### 7. Simulation End

`sc_stop()` was called or the event queue is empty. The kernel runs `end_of_simulation()` callbacks on all modules before exiting.

## Phase Diagram

```
sc_start()
    │
    ▼
 [Initialize]  ← run all processes once
    │
    ▼
 [Evaluate] ←──────────────────────┐
    │                              │
    ▼                              │ (new delta triggers)
 [Update]                          │
    │                              │
    ▼                              │
 [Delta Notify] ──── triggers? ────┘
    │
    │ (no more delta triggers)
    ▼
 [Timed Notify] ← advance sim time to next event
    │
    ▼
 [Evaluate] ← and so on...
```

## Initialization Pitfall: Order Matters

During initialization, process run order is implementation-defined. If your model assumes process A has already set an initial value before process B reads it, you may get incorrect behavior.

**Better practice**: use module `before_end_of_elaboration()` or `start_of_simulation()` callbacks to set initial states deterministically.

```cpp
void start_of_simulation() override {
    // Guaranteed to run after all modules are connected
    // but before the first evaluate phase
    my_signal.write(RESET_VAL);
}
```

## SC_METHOD vs SC_THREAD in the Scheduler

| Property | SC_METHOD | SC_THREAD |
|---|---|---|
| Runs to completion | Yes (no wait mid-body) | No (suspends at wait) |
| Stack preserved between calls | No | Yes |
| Can call `wait()` | No | Yes |
| Typical use | Combinational logic | Sequential state machines |

## Common Pitfalls

- **Reading uninitialized signals**: before initialization runs, signal defaults are their type's default constructor value (false for bool, 0 for int).
- **Assuming initialization order**: do not rely on one process having run before another during initialization.
- **SC_METHOD calling wait()**: this is a run-time error; only SC_THREAD can suspend mid-body.

## Interview Answer

> "The SystemC scheduler cycles through initialization, evaluate, update, and delta-notification phases repeatedly at each time point until quiescence, then advances to the next timed event. SC_THREAD processes can suspend inside the evaluate phase while SC_METHOD processes must run to completion each time they are triggered."
