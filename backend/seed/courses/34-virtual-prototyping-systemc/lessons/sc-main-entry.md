# sc_main and the Simulation Entry Point

Every SystemC program has one mandatory entry point: `sc_main`. Understanding why `sc_main` exists instead of the standard C++ `main`, and what the library does before and after calling it, removes a large class of beginner confusion.

## Why Not `main`?

The SystemC library provides its **own** `main` function inside `libsystemc`. That library `main` performs critical housekeeping before your code runs:

1. Initializes the simulation kernel's internal data structures.
2. Sets up the global time base and scheduler.
3. Installs signal handlers (e.g., for `Ctrl+C` graceful termination).
4. Calls **your** `sc_main(argc, argv)`.
5. After `sc_main` returns, runs end-of-simulation callbacks and cleans up.

If you define your own `main`, you get a **linker error** because `main` is already defined in `libsystemc`. Always use `sc_main`.

## Signature

```cpp
int sc_main(int argc, char* argv[]);
```

- `argc` and `argv` are passed through from the OS — you can use them for command-line parsing exactly as in a normal C++ program.
- The return value propagates back to the OS exit code.

## Phases Inside sc_main

Everything in `sc_main` falls into two conceptual phases:

```
sc_main() {
    // ── ELABORATION PHASE ──────────────────────────────
    //   Instantiate modules, bind ports, configure clocks.
    //   The kernel is NOT running yet.

    sc_clock clk("clk", 10, SC_NS);
    DUT      dut("dut");
    dut.clk(clk);

    // ── SIMULATION PHASE ───────────────────────────────
    //   sc_start() transfers control to the kernel.
    sc_start(100, SC_NS);     // run for 100 ns, then return
    // -- or --
    // sc_start();            // run until sc_stop() is called

    // ── POST-SIMULATION ────────────────────────────────
    //   Analyze results, print reports, check assertions.
    std::cout << "Simulation done at " << sc_time_stamp() << "\n";

    return 0;
}
```

## sc_start Variants

| Call | Behavior |
|------|----------|
| `sc_start()` | Run until `sc_stop()` is called or no more events |
| `sc_start(100, SC_NS)` | Run for exactly 100 ns of simulated time |
| `sc_start(SC_ZERO_TIME)` | Run zero-time delta cycles only (useful to initialize signals) |

Calling `sc_start()` multiple times is legal; the simulation resumes from where it left off.

## A Complete Minimal Example

```cpp
#include <systemc.h>

SC_MODULE(Counter) {
    sc_in<bool>        clk;
    sc_out<sc_uint<8>> count;

    sc_uint<8> cnt;

    SC_CTOR(Counter) : cnt(0) {
        SC_CTHREAD(tick, clk.pos());  // triggered on rising edge
    }

    void tick() {
        while (true) {
            count.write(cnt++);
            wait();               // wait for next rising edge
        }
    }
};

int sc_main(int argc, char* argv[]) {
    // Elaboration
    sc_clock           clk("clk", 10, SC_NS);
    sc_signal<bool>    clk_sig;
    sc_signal<sc_uint<8>> cnt_sig;

    Counter dut("counter");
    dut.clk(clk);
    dut.count(cnt_sig);

    // Simulation
    sc_start(100, SC_NS);   // simulate 10 clock cycles

    // Post-simulation
    std::cout << "Final count: " << cnt_sig.read() << "\n";
    return 0;
}
```

## Terminating Simulation from Inside a Process

A process can end the simulation by calling `sc_stop()`:

```cpp
void my_process() {
    wait(50, SC_NS);
    if (error_detected) {
        SC_REPORT_ERROR("DUT", "Protocol violation detected");
        sc_stop();      // kernel returns to sc_main after this delta
    }
}
```

After `sc_stop()`, the kernel finishes the current delta cycle, then `sc_start()` returns. Code after `sc_start()` in `sc_main` still runs normally.

## Common Pitfalls

- **Defining `main` instead of `sc_main`** — linker error: multiple definition of `main`.
- **Instantiating modules after `sc_start()`** — illegal; modules must be created during elaboration.
- **Forgetting to bind all ports before `sc_start()`** — the kernel reports an unbound port error at simulation start.
- **Calling `wait()` outside a thread context** — only `SC_THREAD` and `SC_CTHREAD` bodies can call `wait()`; `sc_main` itself cannot.

> **Interview answer:** "`sc_main` replaces `main` because the SystemC library provides its own `main` that initializes the simulation kernel before calling `sc_main`. Inside `sc_main` you instantiate and connect modules (elaboration), then call `sc_start()` to hand control to the scheduler (simulation)."
