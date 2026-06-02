# What Are SystemC Processes?

SystemC models hardware by running user-defined **processes** inside a simulation kernel. A process is a C++ function that the kernel calls automatically when certain conditions are met — typically a signal change or a time advance. Understanding processes is the gateway to everything else in SystemC.

## The Simulation Kernel at a Glance

SystemC uses a **discrete-event simulation loop**. Simulation time advances in steps called *delta cycles*. At each step the kernel:

1. Evaluates all processes whose sensitivity conditions are satisfied.
2. Propagates any signal updates into a new delta cycle.
3. Repeats until no more events remain, then advances simulation time.

Processes are the units the kernel schedules. Every piece of hardware behaviour you write lives inside a process.

## Two Fundamental Process Types

SystemC defines two primary process types, registered in the module constructor:

| Type | Registration macro | Can suspend mid-run? | Runs to... |
|---|---|---|---|
| `SC_METHOD` | `SC_METHOD(func)` | No | completion |
| `SC_THREAD` | `SC_THREAD(func)` | Yes (via `wait()`) | termination or next `wait()` |

A third variant, `SC_CTHREAD`, is a clocked thread used in HLS (high-level synthesis) tools and is covered in a later lesson.

## Registering a Process

Processes are registered inside `SC_CTOR` (or an equivalent constructor). You attach a **sensitivity list** that tells the kernel when to wake the process:

```cpp
SC_MODULE(MyModule) {
    sc_in<bool> clk;
    sc_in<bool> data_in;
    sc_out<bool> data_out;

    SC_CTOR(MyModule) {
        // SC_METHOD wakes whenever data_in changes
        SC_METHOD(combinational_logic);
        sensitive << data_in;

        // SC_THREAD runs once; uses wait() internally
        SC_THREAD(sequential_logic);
        sensitive << clk.pos();
    }

    void combinational_logic() { /* ... */ }
    void sequential_logic()    { /* ... */ }
};
```

The sensitivity list is built with `sensitive << signal` (static sensitivity). Dynamic sensitivity is changed at runtime using `next_trigger()` (for methods) or `wait()` arguments (for threads).

## Process Lifecycle

```
Elaboration phase
  └─► Kernel registers all processes
        │
Simulation phase
  ├─► Events trigger ready processes
  ├─► Kernel dispatches processes one at a time
  └─► Process runs (method: to completion; thread: to next wait())
        │
End of simulation
  └─► sc_stop() called; kernel tears down
```

Processes are **not** operating-system threads in the traditional sense (although implementations often use fibers or coroutines under the hood). SystemC guarantees **cooperative scheduling**: only one process runs at a time; no preemption occurs.

## Why Processes Mirror Hardware

Real hardware has:

- **Combinational logic** — output changes instantly when input changes (modelled by `SC_METHOD`).
- **Sequential logic** — output changes only on a clock edge after holding state (modelled by `SC_THREAD` or `SC_CTHREAD`).

This mapping is deliberate. Writing SystemC processes is essentially describing hardware behaviour at a higher abstraction level, which allows fast simulation before RTL synthesis.

## Common Pitfall

Forgetting to add a sensitivity list to an `SC_METHOD` creates a process that **never runs** — a silent bug. Always double-check that every method has at least one signal on its sensitivity list.

> **Interview answer:** A SystemC process is a C++ function registered with the kernel that executes when its sensitivity conditions fire. `SC_METHOD` runs to completion without suspending; `SC_THREAD` can suspend mid-execution via `wait()`. Together they model combinational and sequential hardware behaviour inside the discrete-event simulation loop.
