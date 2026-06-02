# Anatomy of Your First SystemC Model

This lesson walks through a complete, compilable SystemC model line by line. By the end you will be able to read any introductory SystemC source file and explain the role of every construct.

## The Model: A 4-bit Up-Counter with Testbench

We will build two modules:
1. **`Counter`** — the device under test (DUT): a synchronous 4-bit counter with active-high reset.
2. **`Testbench`** — drives the clock and reset, checks the output.

## The Counter Module

```cpp
// counter.h
#pragma once
#include <systemc.h>

SC_MODULE(Counter) {
    // ── Ports ────────────────────────────────────────────
    sc_in<bool>        clk;     // clock input
    sc_in<bool>        reset;   // synchronous reset, active high
    sc_out<sc_uint<4>> count;   // 4-bit output

    // ── Constructor ──────────────────────────────────────
    SC_CTOR(Counter) {
        SC_CTHREAD(do_count, clk.pos());  // sensitive to rising edge
    }

    // ── Process ──────────────────────────────────────────
    void do_count() {
        sc_uint<4> cnt = 0;
        count.write(0);   // initialize output
        wait();           // wait for first rising edge

        while (true) {
            if (reset.read()) {
                cnt = 0;
            } else {
                cnt++;
            }
            count.write(cnt);
            wait();           // wait for next rising edge
        }
    }
};
```

**Anatomy breakdown:**

| Element | Purpose |
|---------|---------|
| `sc_in<bool> clk` | Port: reads a boolean clock signal |
| `sc_in<bool> reset` | Port: reads the reset control signal |
| `sc_out<sc_uint<4>> count` | Port: drives a 4-bit unsigned value |
| `SC_CTHREAD(do_count, clk.pos())` | Registers `do_count` as a clocked thread triggered on rising edge |
| `wait()` inside the thread | Suspends until next trigger (rising edge of clk) |
| `count.write(cnt)` | Schedules the new value; takes effect after the update phase |

## The Testbench Module

```cpp
// testbench.h
#pragma once
#include <systemc.h>

SC_MODULE(Testbench) {
    sc_out<bool>       clk;
    sc_out<bool>       reset;
    sc_in<sc_uint<4>>  count;

    SC_CTOR(Testbench) {
        SC_THREAD(run);
    }

    void run() {
        // Apply reset for 3 cycles
        reset.write(true);
        for (int i = 0; i < 3; ++i) {
            clk.write(false); wait(5, SC_NS);
            clk.write(true);  wait(5, SC_NS);
        }

        // Release reset and count for 20 cycles
        reset.write(false);
        for (int i = 0; i < 20; ++i) {
            clk.write(false); wait(5, SC_NS);
            clk.write(true);  wait(5, SC_NS);

            // Sample count on rising edge
            std::cout << "Time=" << sc_time_stamp()
                      << "  count=" << count.read() << "\n";
        }

        sc_stop();
    }
};
```

## The Top-Level sc_main

```cpp
// main.cpp
#include <systemc.h>
#include "counter.h"
#include "testbench.h"

int sc_main(int argc, char* argv[]) {
    // Signals connecting DUT and testbench
    sc_signal<bool>       clk_sig, rst_sig;
    sc_signal<sc_uint<4>> cnt_sig;

    // Instantiate modules
    Counter   dut("dut");
    Testbench tb("tb");

    // Bind ports to signals
    dut.clk(clk_sig);   tb.clk(clk_sig);
    dut.reset(rst_sig); tb.reset(rst_sig);
    dut.count(cnt_sig); tb.count(cnt_sig);

    // Optional: dump waveforms
    sc_trace_file* tf = sc_create_vcd_trace_file("counter_wave");
    sc_trace(tf, clk_sig, "clk");
    sc_trace(tf, rst_sig, "reset");
    sc_trace(tf, cnt_sig, "count");

    sc_start();   // run until sc_stop() called in testbench

    sc_close_vcd_trace_file(tf);
    return 0;
}
```

## Building and Running

```bash
# Assuming SYSTEMC_HOME is set
g++ -std=c++14 \
    -I${SYSTEMC_HOME}/include \
    -L${SYSTEMC_HOME}/lib-linux64 \
    main.cpp -lsystemc -o counter_sim

./counter_sim
```

Expected output (partial):

```
Time=30 ns  count=1
Time=40 ns  count=2
Time=50 ns  count=3
...
Time=220 ns  count=4   # wraps at 15 → 0 → 1 ...
```

## Key Design Patterns Demonstrated

- **Separate `.h` files per module** — keeps the project navigable.
- **Testbench drives clocks manually** — gives full control over stimulus timing.
- **`sc_stop()` in testbench** — clean simulation termination without hardcoding a time limit in `sc_main`.
- **`sc_trace`** — generates a `.vcd` file viewable in GTKWave or any waveform viewer.

## Common Pitfalls

- **Testbench port directions**: the testbench *drives* clk and reset, so they must be `sc_out`. The DUT receives them as `sc_in`. Swapping directions causes a compile error.
- **`sc_clock` vs. manual clock** — `sc_clock` is convenient but less flexible. Manual clock generation (as shown above) allows non-50% duty cycles and clock gating.
- **Not calling `wait()` before reading inputs in a `SC_CTHREAD`** — the very first `wait()` synchronizes to the first clock edge; without it you read uninitialized signal values.

> **Interview answer:** "A SystemC model consists of `SC_MODULE` classes with typed ports, internal signals connecting sub-modules, and process methods registered with `SC_CTHREAD` or `SC_METHOD`. `sc_main` instantiates the modules, binds their ports to signals, and calls `sc_start()`. A testbench module drives stimulus and calls `sc_stop()` to end the run."
