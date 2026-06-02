# Elaboration vs Simulation Phases

SystemC divides program execution into two sharply distinct phases. Confusing them is the single most common source of mysterious crashes and "why is my signal always 0?" bugs in SystemC code. This lesson draws a clear boundary between the two.

## The Two-Phase Model

```
Program start
     │
     ▼
┌─────────────────────────────────┐
│       ELABORATION PHASE         │
│  • Module constructors run      │
│  • Ports are bound to signals   │
│  • Sensitivity lists built      │
│  • sc_start() NOT yet called    │
└──────────────┬──────────────────┘
               │  sc_start() called
               ▼
┌─────────────────────────────────┐
│       SIMULATION PHASE          │
│  • Kernel scheduler runs        │
│  • Processes execute            │
│  • sc_time advances             │
│  • wait() / notify() active     │
└──────────────┬──────────────────┘
               │  sc_stop() or time limit
               ▼
         Post-simulation
```

## Elaboration Phase

Elaboration runs from the first module instantiation until `sc_start()` is called. During this phase:

- Module constructors (`SC_CTOR`) execute sequentially.
- Ports are bound to signals with `module.port(signal)`.
- `SC_METHOD`, `SC_THREAD`, `SC_CTHREAD` registrations record which function to call when — but do not call them yet.
- `before_end_of_elaboration()` callbacks run automatically (used by TLM socket binding checks).

```cpp
int sc_main(int argc, char* argv[]) {
    // ── All of this is ELABORATION ──────────────────────
    sc_signal<bool> req, ack;
    sc_clock        clk("clk", 10, SC_NS);

    Initiator init("init");
    Target    tgt("tgt");

    init.clk(clk);
    init.req(req);   // port binding happens here
    tgt.req(req);
    tgt.ack(ack);
    init.ack(ack);
    // ───────────────────────────────────────────────────

    sc_start(200, SC_NS);  // ← elaboration ends, simulation begins
    return 0;
}
```

## Simulation Phase

Once `sc_start()` is called, the kernel takes over. The simulation phase follows the **evaluate-update** loop:

1. **Initialize** — every process runs once at time 0 (before any `wait()`).
2. **Evaluate** — all runnable processes execute. Signals are read; new values are scheduled but not yet written.
3. **Update** — pending signal writes are committed. If any signal changed, another evaluate pass runs (a delta cycle).
4. **Advance time** — when no more delta cycles are pending, time advances to the next event.

```cpp
SC_MODULE(Toggle) {
    sc_out<bool> out;
    SC_CTOR(Toggle) { SC_THREAD(run); }

    void run() {
        bool v = false;
        while (true) {
            out.write(v);
            v = !v;
            wait(5, SC_NS);   // ← only legal in simulation phase
        }
    }
};
```

## Delta Cycles

A delta cycle is a zero-time evaluation step used to propagate signal changes without advancing simulated time. Multiple delta cycles can occur at the same `sc_time_stamp()`.

```
Time 10 ns, Δ0: A writes to sig_x
Time 10 ns, Δ1: B reads sig_x (updated), writes to sig_y
Time 10 ns, Δ2: C reads sig_y (updated), no more changes
Time 15 ns, Δ0: next real-time event
```

This mirrors how combinational logic settles in real hardware.

## What Is Illegal in Each Phase

| Action | Elaboration | Simulation |
|--------|-------------|-----------|
| Create `sc_module` instances | Legal | **Illegal** |
| Bind ports to signals | Legal | **Illegal** |
| Call `wait()` | **Illegal** | Legal (threads only) |
| Call `sc_time_stamp()` | Returns 0 | Returns current time |
| Write to `sc_signal` via `.write()` | Legal (initial value) | Legal |
| Call `sc_start()` | Legal (starts simulation) | Re-entrant call is legal |

## The `end_of_elaboration` Callback

Modules can override `end_of_elaboration()` to perform checks just before simulation begins:

```cpp
SC_MODULE(SafeModule) {
    sc_in<bool> enable;

    void end_of_elaboration() override {
        if (enable.bind_count() == 0)
            SC_REPORT_FATAL("SafeModule", "enable port not bound!");
    }
};
```

This is the right place for binding validation, not inside `SC_CTOR`.

## Common Pitfalls

- **Dynamically creating modules in a thread** — crashes the kernel; all modules must exist before `sc_start()`.
- **Reading a signal in `SC_CTOR`** — returns the default-constructed value, not a meaningful simulation value.
- **Binding ports inside a process** — undefined behavior; the port hierarchy is frozen at `sc_start()`.
- **Calling `wait(0, SC_NS)` thinking it does nothing** — it actually inserts a delta cycle and gives other processes a chance to run.

> **Interview answer:** "Elaboration is the setup phase where modules are instantiated and ports are connected; no time passes and no processes run. Simulation begins when `sc_start()` is called — the kernel then schedules processes, advances simulated time, and propagates signal updates through delta cycles. Creating modules after `sc_start()` is illegal."
