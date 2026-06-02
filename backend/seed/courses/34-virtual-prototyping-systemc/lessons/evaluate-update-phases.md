# The Evaluate-Update Cycle

The evaluate-update cycle is the heartbeat of the SystemC kernel. Every delta cycle consists of exactly these two phases, executed in strict order. Understanding them precisely is what separates engineers who can reason about simulation correctness from those who fight mysterious ordering bugs.

## Phase 1: Evaluate

During the evaluate phase, the kernel runs every process that has become **runnable** — either because an event it is sensitive to was notified, or because it was explicitly triggered.

Key rules during evaluation:

- Processes run to their next `wait()` statement (SC_THREAD) or to completion (SC_METHOD).
- A process can **read** the current values of signals and ports.
- A process can **write** to signals, but the write is **not applied immediately**. It is queued as a pending update.
- Multiple processes may run in this phase. Their relative order within one delta cycle is implementation-defined (not guaranteed by the standard).

```cpp
void adder_process() {
    // Evaluate phase: reads current a and b, queues result to sum
    sum.write(a.read() + b.read());
    // sum still has its OLD value here — the write is pending
}
```

## Phase 2: Update

Once all runnable processes have completed their evaluate step, the kernel enters the update phase:

- All pending signal writes are committed — signal storage is updated.
- If any signal's new value differs from its old value, the processes sensitive to that signal are made runnable for the **next** evaluate phase (next delta cycle).
- No user process code runs during the update phase.

```cpp
// After update phase completes:
// sum now holds a.read() + b.read()
// Any process sensitive to 'sum' is queued to run next delta
```

## The Full Loop

```
┌─────────────────────────────────────────────────────┐
│  Simulation time T                                   │
│                                                      │
│  ┌─ Delta 0 ────────────────────────────────────┐   │
│  │  Evaluate: run all triggered processes        │   │
│  │  Update:   commit pending writes              │   │
│  │  Any new triggers? → go to Delta 1            │   │
│  └──────────────────────────────────────────────┘   │
│  ┌─ Delta 1 ────────────────────────────────────┐   │
│  │  Evaluate → Update → any triggers? → Delta 2  │   │
│  └──────────────────────────────────────────────┘   │
│  ... until no new triggers (quiescence)              │
│  → Advance to next event time T'                     │
└─────────────────────────────────────────────────────┘
```

## Worked Example: AND Gate

```cpp
SC_MODULE(AndGate) {
    sc_in<bool>  a, b;
    sc_out<bool> y;

    void compute() {
        y.write(a.read() & b.read());
    }

    SC_CTOR(AndGate) {
        SC_METHOD(compute);
        sensitive << a << b;
    }
};
```

Suppose at t=0, `a=0, b=0`. Then at t=5 ns, `a` is driven to 1:

1. **t=5 ns, evaluate delta 0**: `compute()` runs. Reads `a=1, b=0`, writes `y=0` (pending — same as current, no change).
2. **t=5 ns, update delta 0**: `y` stays 0. No new triggers. Quiescence.

Now at t=10 ns, `b` is driven to 1:

1. **t=10 ns, evaluate delta 0**: reads `a=1, b=1`, writes `y=1` (pending — new value!).
2. **t=10 ns, update delta 0**: `y` becomes 1. Processes sensitive to `y` are triggered.
3. **t=10 ns, evaluate delta 1**: downstream processes run.

## Why Process Ordering in Evaluate Doesn't Matter

Because all reads see the *pre-update* values and all writes are pending, two processes reading the same signal in the same delta will always get the same answer, regardless of which runs first. This is the core correctness guarantee of the evaluate-update model.

## Common Pitfalls

- **Relying on intra-delta ordering**: never assume process A runs before process B within the same evaluate phase. The standard does not guarantee it.
- **Reading a signal you just wrote**: within the same `SC_METHOD`, a write to a signal and a subsequent read of that same signal returns the **old** value, not the new one. The write is still pending.

```cpp
void broken() {
    sig.write(1);
    int v = sig.read();  // still reads OLD value — 0, not 1
}
```

## Interview Answer

> "Each delta cycle has two phases: evaluate, where all runnable processes execute and queue their signal writes as pending; and update, where those writes are committed and newly triggered processes are identified. No process runs during update, which ensures all reads within one evaluate see a consistent snapshot of the previous state."
