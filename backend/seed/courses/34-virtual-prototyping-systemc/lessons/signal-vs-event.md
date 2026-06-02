# sc_signal vs sc_event: Value vs Notification

`sc_signal<T>` and `sc_event` are both wake-up mechanisms in SystemC, but they serve fundamentally different purposes. Choosing between them is one of the first design decisions when connecting SystemC modules.

## Core Difference at a Glance

| Property | `sc_signal<T>` | `sc_event` |
|---|---|---|
| Carries a value | Yes — readable anytime | No |
| Memory after notification | Yes — holds last written value | No — notification vanishes |
| Notifies on every write | Only if value *changes* | Always, on every `notify()` |
| Multiple simultaneous waiters | Yes | Yes |
| Simulation visibility (VCD) | Yes | Not by default |
| Suitable for waveform tracing | Yes | No |

## sc_signal: Value-Centric Communication

`sc_signal<T>` models a wire. It is appropriate when:

- A *current state* must be readable at any time.
- Communication is data-driven (the receiver wants to know the value, not just that something happened).
- You need waveform tracing for debugging.

```cpp
sc_signal<bool> ready;

// Writer:
ready.write(true);

// Reader (at any time):
bool r = ready.read();   // always valid; returns last committed value

// Sensitivity:
sensitive << ready;      // fires ONLY when value changes (false→true or true→false)
```

**Critical**: `sc_signal` does NOT notify if the written value equals the current value. Writing `true` when the signal is already `true` produces no notification.

```cpp
sc_signal<int> sig;
sig.write(42);   // first write: notifies (0 → 42)
sig.write(42);   // second write: NO notification (42 → 42, no change)
sig.write(43);   // third write: notifies (42 → 43)
```

## sc_event: Notification-Centric Synchronization

`sc_event` models a trigger or interrupt. It is appropriate when:

- You only need to signal that *something happened*, not what happened.
- The notification must fire even if no value changed.
- You are synchronizing threads (handshake, semaphore, timeout).

```cpp
sc_event data_ready;

// Notifier:
data_ready.notify(SC_ZERO_TIME);   // always fires

// Waiter:
wait(data_ready);                  // wakes on next notification
// No value to read — must use another channel for the data
```

## sc_buffer: The Middle Ground

`sc_buffer<T>` behaves like `sc_signal<T>` but notifies on *every* write, even if the value did not change:

```cpp
sc_buffer<int> buf;
buf.write(42);   // notifies
buf.write(42);   // ALSO notifies (unlike sc_signal)
```

Use `sc_buffer` when the *act of writing* matters as a trigger, independent of value change — for example, a "strobe" or pulse pattern.

## Combined Pattern: Event + Signal

A common idiom pairs both: an event as a "doorbell" and a signal (or plain variable) as the "message":

```cpp
SC_MODULE(Producer) {
    sc_out<int>  data;
    sc_event     data_valid;

    void produce() {
        data.write(42);                     // set value
        data_valid.notify(SC_ZERO_TIME);    // ring the bell
    }
};

SC_MODULE(Consumer) {
    sc_in<int>  data;
    sc_event*   data_valid;

    void consume() {
        wait(*data_valid);          // wait for doorbell
        int d = data.read();        // read the value
        std::cout << "Got: " << d << "\n";
    }
};
```

This pattern avoids the "missed notification" problem: even if the value in the signal did not change, the explicit event ensures the consumer wakes up.

## Decision Guide

```
Need to READ the current value at any time?
    YES → sc_signal<T>
    NO  → sc_event

Must wake consumer even when value didn't change?
    YES → sc_event (or sc_buffer)
    NO  → sc_signal<T>

Need waveform tracing?
    YES → sc_signal<T>
    NO  → either works

Modeling a hardware wire or bus?
    YES → sc_signal<T>
    NO  → sc_event
```

## Common Pitfalls

1. **Relying on sc_signal to pulse**: writing `1` then `0` in the same delta to an `sc_signal<bool>` — the intermediate `1` may never be seen by other processes since both writes collapse.
2. **Using sc_event for data**: there is no value attached; pairing with a shared variable without synchronization can create races.
3. **Expecting sc_signal to notify on no-change writes**: it will not, which can cause a consumer to miss an "update" if the new value happens to equal the old one.

> **Interview answer:** `sc_signal<T>` is a value-carrying, delta-buffered wire that only notifies on value change and is always readable, while `sc_event` is a valueless, one-shot trigger that fires on every `notify()` regardless of state — use signals for data communication and events for synchronization.
