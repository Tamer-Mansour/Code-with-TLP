# next_trigger() for Dynamic Sensitivity

`next_trigger()` is the `SC_METHOD` counterpart to `wait()` in `SC_THREAD`. It lets a method **change what it will be triggered by** the next time it runs — without suspending mid-execution.

## Why Dynamic Sensitivity Matters

Static sensitivity (`sensitive << sig`) means the method runs every time any listed signal changes, regardless of current context. Dynamic sensitivity lets the method say: *"right now I only care about this particular event; trigger me only for that."*

This is essential for:

- Power modelling (only wake on certain conditions to count power states).
- Protocol monitors that track state across multiple transactions.
- Replacing `SC_THREAD` with `SC_METHOD` in performance-critical code.

## Syntax

```cpp
// After computing the result, set what fires next:
next_trigger(event);                        // a specific sc_event
next_trigger(event_a | event_b);            // OR of events
next_trigger(event_a & event_b);            // AND of events
next_trigger(10, SC_NS);                    // pure timeout
next_trigger(10, SC_NS, event);             // timeout OR event
next_trigger();                             // reset to static sensitivity
```

Calling `next_trigger()` with no arguments **restores** the static sensitivity list for the next activation.

## Worked Example: Simple Protocol Monitor

```cpp
SC_MODULE(SpiMonitor) {
    sc_in<bool> cs_n;    // chip-select, active low
    sc_in<bool> sclk;
    sc_in<bool> mosi;

    int  bit_count;
    uint8_t shift_reg;

    SC_CTOR(SpiMonitor) : bit_count(0), shift_reg(0) {
        SC_METHOD(monitor);
        sensitive << cs_n.negedge_event();  // start idle, wake on CS assert
    }

    void monitor() {
        if (!cs_n.read()) {
            // CS just asserted — start capturing bits
            bit_count = 0; shift_reg = 0;
            next_trigger(sclk.posedge_event() | cs_n.posedge_event());
        } else if (cs_n.read()) {
            // CS deasserted — transaction complete
            std::cout << "SPI byte: 0x" << std::hex << (int)shift_reg << "\n";
            next_trigger(cs_n.negedge_event());   // wait for next CS
        } else {
            // Must be a SCLK edge — sample MOSI
            shift_reg = (shift_reg << 1) | mosi.read();
            bit_count++;
            if (bit_count < 8)
                next_trigger(sclk.posedge_event() | cs_n.posedge_event());
            else
                next_trigger(cs_n.posedge_event());  // wait for CS release
        }
    }
};
```

Without `next_trigger()` this logic would need an `SC_THREAD` with `wait()` calls, carrying a much higher simulation overhead for a passive monitor.

## next_trigger() vs Static Sensitivity: Precedence

When `next_trigger()` is called inside a method body, it **overrides** the static sensitivity list **for exactly one activation**. After that single activation, control reverts to static sensitivity unless `next_trigger()` is called again.

```
Activation N:
  method runs → calls next_trigger(event_X)
  → next activation: triggered by event_X (not static list)

Activation N+1:
  method runs → does NOT call next_trigger()
  → next activation: back to static sensitivity list
```

## Event AND Semantics

`next_trigger(a & b)` creates an event that fires only when both `a` and `b` have occurred since the last trigger. This is a rare but useful pattern for synchronisation barriers:

```cpp
// Wake only after both read_done and write_done have fired
next_trigger(read_done_event & write_done_event);
```

## Common Pitfall: Forgetting next_trigger() in a Branch

If any code path inside the method does **not** call `next_trigger()`, that path falls through to static sensitivity. This is often intentional, but forgetting it in a branch where you intended dynamic sensitivity creates an always-sensitive method that fires far too often.

```cpp
void my_method() {
    if (state == IDLE) {
        next_trigger(start.posedge_event());
    }
    // BUG: if state != IDLE, falls back to static sensitivity
    // Add else clause with appropriate next_trigger()
}
```

## Performance Benefit

A well-crafted `SC_METHOD` with `next_trigger()` can replace an `SC_THREAD` running a full state machine while:

- Eliminating coroutine stack save/restore overhead.
- Reducing the number of unnecessary process evaluations.
- Making the module more amenable to formal tools that prefer acyclic control flow.

> **Interview answer:** `next_trigger()` changes the trigger condition of an `SC_METHOD` for its next activation, providing dynamic sensitivity equivalent to what `wait(event)` gives an `SC_THREAD`. It takes effect after the current method body completes and lasts for exactly one subsequent activation, after which static sensitivity resumes unless `next_trigger()` is called again.
