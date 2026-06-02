# What Is sc_signal?

`sc_signal<T>` is SystemC's fundamental communication primitive for modeling wire-like connections between modules. It acts as a shared variable with simulation-aware semantics: writes take effect only at the next delta cycle, preserving the concurrent nature of hardware description.

## Core Concept

In RTL hardware, a wire carries a value that all connected components can read simultaneously. `sc_signal<T>` models this with three key guarantees:

- **Determinism**: multiple writers in the same delta step do not produce race conditions — the simulator detects multi-driver conflicts.
- **Delta-cycle update**: a value written with `write()` is not visible via `read()` until the next delta cycle, so concurrent processes see a consistent snapshot.
- **Change notification**: processes sensitive to the signal are re-activated automatically when the value changes.

## Basic Usage

```cpp
#include <systemc.h>

SC_MODULE(Inverter) {
    sc_in<bool>  in;
    sc_out<bool> out;

    SC_CTOR(Inverter) {
        SC_METHOD(invert);
        sensitive << in;       // re-run whenever 'in' changes
    }

    void invert() {
        out.write(!in.read()); // write is buffered; takes effect next delta
    }
};

int sc_main(int, char**) {
    sc_signal<bool> sig_a, sig_b;

    Inverter inv("inv");
    inv.in(sig_a);
    inv.out(sig_b);

    sig_a.write(false);
    sc_start(10, SC_NS);
    return 0;
}
```

## Template Parameter

`sc_signal<T>` works with any type that supports `==` comparison (needed to detect value changes):

| T | Typical Use |
|---|-------------|
| `bool` | single-bit wire |
| `sc_logic` | 4-valued logic (0, 1, X, Z) |
| `sc_uint<N>` | N-bit unsigned bus |
| `int`, `double` | algorithmic modeling |

## Read / Write Semantics

```cpp
sc_signal<int> counter;

// In a process:
int current = counter.read();   // reads current (committed) value
counter.write(current + 1);     // schedules update; not visible yet
// counter.read() still returns 'current' in this delta
```

The separation between `read()` and `write()` mirrors how real flip-flops latch values on a clock edge — the output does not change mid-cycle.

## Common Pitfalls

1. **Reading your own write in the same delta**: The new value is not visible until delta+1. Design processes that depend on the new value must wait for the next activation.
2. **Multiple drivers**: `sc_signal` supports only one writer. Use `sc_signal_resolved` or `sc_signal<sc_logic>` for tri-state/wired-OR buses.
3. **Forgetting `sensitive`**: If a `SC_METHOD` is not sensitive to the signal it reads, it will never re-run when the signal changes.

## sc_signal vs a Plain Variable

| Feature | Plain C++ variable | `sc_signal<T>` |
|---|---|---|
| Concurrent-safe reads | No | Yes (delta buffering) |
| Automatic process wakeup | No | Yes |
| Detects multi-driver | No | Yes |
| Hardware semantics | No | Yes |

## Worked Example: Two-Process Feedback

```cpp
SC_MODULE(Feedback) {
    sc_signal<int> x;

    SC_CTOR(Feedback) {
        SC_METHOD(producer); sensitive << x;
        SC_METHOD(consumer); sensitive << x;
    }

    void producer() { /* writes x */ }
    void consumer() { int v = x.read(); /* sees committed value */ }
};
```

Both processes see the *same* committed value of `x` within one delta cycle, regardless of execution order — this is the cornerstone of repeatable simulation.

> **Interview answer:** `sc_signal<T>` is a delta-cycle-buffered channel that models a hardware wire; writes are not visible until the next delta so concurrent processes always read a consistent snapshot, and any change automatically wakes sensitive processes.
