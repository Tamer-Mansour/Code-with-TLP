# What Is a Delta Cycle?

The delta cycle is one of the most important — and most misunderstood — concepts in SystemC. It is the mechanism that gives signal updates their characteristic "one step behind" behavior and ensures that concurrent processes interact in a well-defined, repeatable order.

## The Problem Delta Cycles Solve

Imagine two processes running at the same simulation timestamp. Process A reads signal X and writes signal Y. Process B reads signal Y and writes signal Z. If we naively let them run in any order, the result depends on scheduling — a race condition in the simulation itself.

Delta cycles solve this by separating **evaluation** from **update**: all processes first read current values, then all signal updates take effect, then the cycle repeats.

## What Is a Delta Cycle?

A delta cycle is a pair of phases — evaluate, then update — that happens at a single simulation timestamp. Simulation time does not advance between delta cycles. They are indexed by a counter (delta 0, delta 1, delta 2, …) that resets to zero each time real simulation time advances.

```
Simulation time = 10 ns
  Delta 0: evaluate all ready processes → some signals change
  Delta 0: update phase → new signal values committed
  Delta 1: evaluate processes sensitive to changed signals → more changes
  Delta 1: update phase → committed
  Delta 2: evaluate → no more changes → quiescence reached
Simulation time advances to next event (e.g. 20 ns)
```

## Visualizing the Delta Counter

You can read the current delta count during simulation:

```cpp
void my_process() {
    std::cout << "Time=" << sc_time_stamp()
              << " Delta=" << sc_delta_count() << "\n";
}
```

## A Concrete Example

```cpp
SC_MODULE(Ripple) {
    sc_signal<int> a, b, c;

    void p1() { b.write(a.read() + 1); }
    void p2() { c.write(b.read() * 2); }

    SC_CTOR(Ripple) {
        SC_METHOD(p1); sensitive << a;
        SC_METHOD(p2); sensitive << b;
        a.write(0);    // triggers p1 at delta 0
    }
};
```

Trace at time 0:
- **Delta 0, evaluate**: `p1` runs, reads `a=0`, writes `b=1` (pending)
- **Delta 0, update**: `b` becomes 1 — `p2` is now triggered
- **Delta 1, evaluate**: `p2` runs, reads `b=1`, writes `c=2` (pending)
- **Delta 1, update**: `c` becomes 2 — no new triggers
- Quiescence: simulation time advances

## Delta Cycles vs. Real Time

Delta cycles are invisible to the outside world — they carry no physical time. From the perspective of the simulated hardware, everything at "10 ns, delta 0" through "10 ns, delta 5" happens at the *same instant*: 10 ns.

| Property | Delta cycle | Real time |
|---|---|---|
| Advances simulation clock | No | Yes |
| Allows signal propagation | Yes | N/A |
| Visible to `sc_time_stamp()` | No | Yes |
| Can loop indefinitely | Yes (danger!) | No |

## Infinite Delta Loops

A common pitfall: if process A notifies process B with `SC_ZERO_TIME` and B notifies A likewise, the delta counter grows without bound and the simulation never progresses. SystemC provides no built-in detection — you must design your model to guarantee convergence.

```cpp
// DANGEROUS — infinite delta loop
void a_proc() { evt_b.notify(SC_ZERO_TIME); wait(evt_a); }
void b_proc() { evt_a.notify(SC_ZERO_TIME); wait(evt_b); }
```

## Interview Answer

> "A delta cycle is one evaluate-update pair at a fixed simulation timestamp. It lets all processes read current signal values before any writes take effect, eliminating race conditions. Multiple delta cycles may occur at the same simulation time until the system reaches quiescence, at which point real simulation time advances."
