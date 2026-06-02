# What Is sc_event?

`sc_event` is SystemC's low-level synchronization primitive. Unlike `sc_signal`, it carries no value — it is a pure notification mechanism. A process can *wait* for an event, and another process (or channel) can *notify* it, causing any waiting processes to be scheduled for execution.

## Mental Model

Think of `sc_event` as a starting pistol: it fires once, wakes all runners who were listening, and is then silent until fired again. It has no memory of past firings — a process that calls `wait(e)` *after* `e` has already been notified will simply block until the next notification.

## Declaring and Using sc_event

```cpp
#include <systemc.h>

SC_MODULE(Producer) {
    sc_event done_event;   // declared as a member

    SC_CTOR(Producer) {
        SC_THREAD(produce);
    }

    void produce() {
        wait(10, SC_NS);          // time-based wait
        std::cout << "Produced at " << sc_time_stamp() << "\n";
        done_event.notify();      // immediate notification
    }
};

SC_MODULE(Consumer) {
    sc_in_clk           clk;
    sc_event*           done;    // pointer set externally

    SC_CTOR(Consumer) {
        SC_THREAD(consume);
    }

    void consume() {
        wait(*done);              // block until done_event fires
        std::cout << "Consumed at " << sc_time_stamp() << "\n";
    }
};
```

## The Three Notification Flavors

| Method | When Consumer Wakes |
|---|---|
| `e.notify()` | Immediately, in the same delta step |
| `e.notify(SC_ZERO_TIME)` | Next delta cycle |
| `e.notify(10, SC_NS)` | After 10 ns of simulated time |

Detailed rules are covered in the "Immediate, Delta, and Timed Notification" lesson; the key takeaway here is that `sc_event` supports all three scheduling modes through the same `notify()` call.

## Waiting for Events in Processes

`SC_THREAD` and `SC_CTHREAD` can suspend with `wait()`. `SC_METHOD` processes cannot call `wait()` but can be made sensitive to an event via the static sensitivity list.

```cpp
// In an SC_THREAD:
sc_event e1, e2;

void my_thread() {
    wait(e1);                          // wait for e1
    wait(e1 | e2);                     // wait for either
    wait(e1 & e2);                     // wait for both (same delta)
    wait(5, SC_NS, e1);               // wait up to 5 ns or until e1
}
```

## sc_event_queue

When multiple notifications must be queued (so none is lost), use `sc_event_queue`:

```cpp
sc_event_queue eq;
eq.notify(1, SC_NS);
eq.notify(3, SC_NS);  // both notifications will be delivered
```

A plain `sc_event` with two `notify(t)` calls where the second fires before the first is processed will *cancel* the first — only the earlier-scheduled one survives. `sc_event_queue` does not have this limitation.

## Common Pitfalls

1. **Lost notification**: if no process is waiting when `notify()` is called, the event is gone. Use a flag variable plus an event if you need persistence:
   ```cpp
   bool flag = false;
   sc_event ev;

   // sender:
   flag = true;
   ev.notify();

   // receiver:
   if (!flag) wait(ev);
   ```
2. **Immediate notify in SC_METHOD**: calling `notify()` inside an `SC_METHOD` causes the sensitive processes to run in the *same* evaluation phase, which can create infinite loops if they notify each other.
3. **Pointer vs reference**: always pass `sc_event` by reference (`wait(e)`), not by value — copying an event is not well-defined.

## sc_event vs sc_signal

| | `sc_event` | `sc_signal<T>` |
|---|---|---|
| Carries a value | No | Yes |
| Persistent after notify | No | Yes (holds last value) |
| Multiple waiters | Yes | Yes (via sensitivity) |
| Use case | Synchronization | Data communication |

> **Interview answer:** `sc_event` is a value-less synchronization primitive in SystemC; a process blocks on `wait(e)` and is rescheduled when another process or channel calls `e.notify()`, which can be immediate, delta-delayed, or time-delayed.
