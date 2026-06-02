# SC_METHOD: Run-to-Completion Processes

`SC_METHOD` is the workhorse of combinational and simple reactive logic in SystemC. Once triggered, it runs its C++ function body from start to finish without any pause. The kernel cannot interrupt it, and it cannot call `wait()`.

## How SC_METHOD Works

When an event on the sensitivity list fires, the kernel places the method on the **runnable queue**. When the kernel dispatches it:

1. The C++ function runs from the first line to the last (`return`).
2. Control returns to the kernel.
3. The kernel moves on to the next runnable process.

The entire execution is **instantaneous** from the simulation-time perspective — it consumes zero simulated time (though it may advance delta cycles if it writes signals).

## Defining and Registering

```cpp
SC_MODULE(Adder) {
    sc_in<sc_uint<8>>  a, b;
    sc_out<sc_uint<9>> sum;

    SC_CTOR(Adder) {
        SC_METHOD(compute);
        sensitive << a << b;   // wake whenever a or b changes
    }

    void compute() {
        sum.write(a.read() + b.read());
    }
};
```

- `SC_METHOD(compute)` registers the function.
- `sensitive << a << b` adds both ports to the static sensitivity list.
- Every time `a` or `b` changes, `compute` re-runs completely.

## Static vs Dynamic Sensitivity

By default, `SC_METHOD` uses **static sensitivity**: the sensitivity list is fixed at elaboration time. You can override this at runtime using `next_trigger()` — covered in detail in the "next_trigger() for Dynamic Sensitivity" lesson.

```cpp
void compute() {
    if (enable.read()) {
        out.write(a.read() & b.read());
        next_trigger(a.value_changed_event() | b.value_changed_event());
    } else {
        out.write(0);
        next_trigger(enable.value_changed_event());
    }
}
```

## Modelling Combinational Logic

`SC_METHOD` is the natural fit for combinational logic because:

- Combinational logic has no internal state between evaluations — same inputs always produce same outputs.
- There is no need to suspend: the output is computed in one shot.
- RTL synthesis tools can directly infer combinational blocks from `SC_METHOD` bodies (in SystemC-based HLS flows).

**Timing model:**

```
t=0: a changes
  └─► compute() fires in delta cycle
        └─► sum updated in delta+1
t still 0 (no real time consumed)
```

## Rules and Restrictions

- **Cannot call `wait()`** — doing so throws a runtime error (`sc_report_handler` fatal).
- **No loops that wait for events** — if you need to loop across time, use `SC_THREAD`.
- The function **must return** (no infinite loops).
- **All signals read** inside the function should ideally be on the sensitivity list; missing one creates a simulation/synthesis mismatch.

## Common Pitfall: Missing Sensitivity

```cpp
// BUG: b is not on the sensitivity list
SC_CTOR(Adder) {
    SC_METHOD(compute);
    sensitive << a;   // missing b!
}

void compute() {
    sum.write(a.read() + b.read());  // b read but not triggering
}
```

`compute` fires only when `a` changes, so a change to `b` alone goes unnoticed. This is one of the most frequent simulation bugs in SystemC.

## Performance Advantage

Because `SC_METHOD` has no coroutine or fiber overhead (no stack save/restore), it executes faster than `SC_THREAD`. For large designs with thousands of combinational blocks, this difference is significant. Prefer `SC_METHOD` whenever a process does not need to suspend.

> **Interview answer:** `SC_METHOD` is a run-to-completion process registered with the kernel via `SC_METHOD(func)`. It executes its entire function body in zero simulated time whenever its sensitivity list fires, cannot call `wait()`, and is the correct model for combinational logic. Missing signals from the sensitivity list is its most common pitfall.
