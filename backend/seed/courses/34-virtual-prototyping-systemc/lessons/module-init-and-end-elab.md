# before_end_of_elaboration and end_of_elaboration

SystemC defines a precise lifecycle for a simulation: elaboration, simulation, and post-simulation. Between the point when all constructors finish and when `sc_start()` actually begins scheduling processes, the kernel fires a sequence of elaboration callbacks. Two of the most useful are `before_end_of_elaboration` and `end_of_elaboration`.

## The Elaboration Lifecycle

```
sc_main() starts
  → All sc_module constructors called (hierarchy built, ports bound, processes registered)
  → before_end_of_elaboration() called on every sc_object (depth-first)
  → Port binding validation performed by kernel
  → end_of_elaboration() called on every sc_object (depth-first)
  → start_of_simulation() called
  → sc_start() begins event scheduling
  → ... simulation runs ...
  → end_of_simulation() called
sc_main() returns
```

## before_end_of_elaboration

This callback fires *before* the kernel validates port bindings. That makes it the right place for:

- **Dynamic port creation or binding** — adding ports whose existence depends on configuration.
- **Connecting optional ports** — if a port is conditionally used, you can inspect it here and bind it to a stub if it was not connected.
- **Registering additional processes** — though this is uncommon and should be avoided in most designs.

```cpp
SC_MODULE(OptionalMonitor) {
    sc_port<sc_signal_in_if<bool>, 0, SC_ZERO_OR_MORE_BOUND> probe;
    // sc_port with 0 min binding — allowed to stay unbound

    void before_end_of_elaboration() override {
        // If probe was not connected, skip adding the trace process
        if (probe.size() == 0) return;
        SC_METHOD(sample);
        sensitive << probe;
    }

    void sample() { /* log probe value */ }
};
```

## end_of_elaboration

This callback fires *after* the kernel has validated all port bindings. At this point you know the design is structurally complete and consistent. Typical uses:

- **Opening trace files** and calling `sc_trace()` to register signals — now that all signals exist and are bound.
- **Printing the design hierarchy** for documentation or regression logging.
- **Checking design parameters** across module boundaries (e.g., confirming that connected FIFOs agree on data width).
- **Allocating large simulation buffers** whose size depends on the fully resolved hierarchy.

```cpp
SC_MODULE(TraceableTop) {
    sc_signal<int>   data_bus;
    sc_trace_file*   tf = nullptr;
    Cpu              cpu;
    Memory           mem;

    SC_CTOR(TraceableTop) : cpu("cpu"), mem("mem") {
        cpu.data(data_bus);
        mem.data(data_bus);
    }

    void end_of_elaboration() override {
        tf = sc_create_vcd_trace_file("dump");
        sc_trace(tf, data_bus, data_bus.name());
        sc_trace(tf, cpu.pc,   cpu.pc.name());
    }

    ~TraceableTop() {
        if (tf) sc_close_vcd_trace_file(tf);
    }
};
```

## start_of_simulation and end_of_simulation

Two additional callbacks complete the picture:

| Callback | When | Typical Use |
|---|---|---|
| `start_of_simulation()` | Just before first delta cycle | Reset behavioral state, print banner |
| `end_of_simulation()` | After `sc_start()` returns | Print statistics, close files, check coverage |

## Override Syntax

All four callbacks are virtual methods on `sc_module`. Override them with the `override` keyword to catch signature typos at compile time:

```cpp
void before_end_of_elaboration() override { ... }
void end_of_elaboration()        override { ... }
void start_of_simulation()       override { ... }
void end_of_simulation()         override { ... }
```

## Common Pitfalls

- **Driving signals in `end_of_elaboration`.**  The scheduler is not running yet; signal updates issued here do not trigger delta cycles. Use `start_of_simulation` for initial signal values instead.
- **Registering `SC_METHOD` or `SC_THREAD` in `end_of_elaboration`.** Processes must be registered before `end_of_elaboration` is called (either in the constructor or in `before_end_of_elaboration`). Attempting to add a process in `end_of_elaboration` is a runtime error in many kernels.
- **Forgetting `override`.** If you mistype the callback name (e.g., `End_of_elaboration`), the virtual call is silently not made. `override` turns this into a compile error.
- **Opening trace files in the constructor.** Signals may not yet be fully bound; `end_of_elaboration` is the correct and safe location.

> **Interview answer:** `before_end_of_elaboration` fires before the kernel validates port bindings and is used for conditional/dynamic port connections. `end_of_elaboration` fires after binding validation and is the correct place to open trace files and check cross-module consistency. Both are virtual methods on `sc_module` that you override to hook into the elaboration lifecycle.
