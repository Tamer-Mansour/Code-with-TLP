# Simulation Time vs Wall-Clock Time

One of the first confusions newcomers face with SystemC is the difference between **simulation time** and **wall-clock time**. They are completely independent concepts and mixing them up leads to fundamental misunderstandings of what your model is doing.

## Simulation Time

Simulation time is the *virtual* timeline your hardware design lives in. It is an abstract counter maintained by the SystemC kernel, expressed in hardware-meaningful units like nanoseconds, picoseconds, or clock cycles. Simulation time:

- Starts at zero when `sc_start()` is called.
- Advances only when the event queue is empty at the current time step.
- Can be queried at any point with `sc_time_stamp()`.
- Is deterministic — the same model always produces the same sequence of events.

```cpp
SC_MODULE(Timer) {
    sc_in<bool> clk;
    void count() {
        std::cout << "Rising edge at simulation time: "
                  << sc_time_stamp() << "\n";
    }
    SC_CTOR(Timer) {
        SC_METHOD(count);
        sensitive << clk.pos();
    }
};
```

If this clock runs at 100 MHz (period = 10 ns), the simulator might print timestamps of 10 ns, 20 ns, 30 ns… regardless of how long your laptop takes to compute them.

## Wall-Clock Time

Wall-clock time is how long your simulation *program* takes to execute on real hardware — what you measure with a stopwatch. It depends on:

- CPU speed and cache behavior.
- Model complexity (number of processes, signal connections).
- Operating system scheduling.
- The SystemC kernel's own overhead.

A simulation covering 1 millisecond of virtual time might complete in 2 seconds of wall-clock time, or 200 milliseconds, depending on workload density.

## Why They Must Be Independent

The separation is intentional and critical:

1. **Repeatability**: simulation results must not depend on how fast the host machine is.
2. **Speed flexibility**: you can simulate a 1 GHz processor's behavior on a 3 GHz host — or a slow IoT peripheral on a fast server.
3. **Abstraction**: transaction-level models (TLM) deliberately model behavior at a coarser time granularity (bus transactions rather than individual cycles), compressing simulation time dramatically.

## The Speed Ratio

Designers often talk about **simulation speed** as a ratio:

```
Simulation speed = simulated_time / wall_clock_time
```

A ratio of 0.1 means: 1 second of wall time simulates 100 ms of hardware time. TLM models routinely achieve 10x–1000x faster ratios than RTL models because they skip cycle-accurate bookkeeping.

## Controlling Simulation Time

```cpp
sc_start(100, SC_NS);    // run until simulation time reaches 100 ns
sc_start();              // run until no more events (simulation ends naturally)
sc_stop();               // request orderly shutdown from within a process
```

## Common Pitfalls

- **Using real `sleep()` calls inside processes**: this blocks the host thread but does NOT advance simulation time. Never use `sleep()` inside an `SC_THREAD` or `SC_METHOD`.
- **Expecting timing accuracy**: simulation time is only as accurate as your model. If you annotate a bus transfer with `wait(10, SC_NS)` but the real bus takes 12 ns, your model will under-report latency.
- **Confusing `sc_time_stamp()` with host time**: they have no fixed relationship.

## Interview Answer

> "Simulation time is the abstract virtual timeline the model operates in, measured in hardware units like nanoseconds. Wall-clock time is how long the simulation program takes to run on the host machine. They are completely independent — the same model always produces the same simulation-time results regardless of host speed."
