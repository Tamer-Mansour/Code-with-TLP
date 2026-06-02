# Clock and Reset Distribution

Every synchronous digital design has a clock and a reset. In a VP you must model both faithfully — firmware often reads clock-derived values (tick counts, baud divisors) and relies on reset to put peripherals into a known state before use.

## Modeling Clocks with `sc_clock`

`sc_clock` is a built-in SystemC signal that toggles at a fixed frequency:

```cpp
sc_core::sc_clock clk("clk", 20.833, sc_core::SC_NS); // 48 MHz
```

Modules connect to the clock through an `sc_in<bool>` port:

```cpp
SC_MODULE(Timer) {
    sc_core::sc_in<bool> clk;
    sc_core::sc_in<bool> rst_n;

    SC_CTOR(Timer) {
        SC_METHOD(tick);
        sensitive << clk.pos(); // react on rising edge
    }

    void tick() {
        if (!rst_n.read()) { count = 0; return; }
        ++count;
    }
    uint32_t count = 0;
};
```

## Multiple Clock Domains

Real SoCs have many clock domains. Model them with multiple `sc_clock` instances:

```cpp
sc_core::sc_clock sys_clk("sys_clk", 20, sc_core::SC_NS);   // 50 MHz
sc_core::sc_clock per_clk("per_clk", 100, sc_core::SC_NS);  // 10 MHz
sc_core::sc_clock adc_clk("adc_clk", 250, sc_core::SC_NS);  // 4 MHz
```

Connect each module to the appropriate clock domain in `sc_main`.

## Clock Domain Crossing (CDC)

When a signal crosses from one clock domain to another, data can be metastable. In a VP:

- If you need **accurate CDC modeling**, insert a two-flop synchronizer module.
- For **LT (loosely timed)** VPs, ignore CDC and use direct signal connections — the goal is functional correctness, not timing closure.

```cpp
// Two-flop synchronizer (for AT/cycle-accurate VPs)
SC_MODULE(Sync2FF) {
    sc_core::sc_in<bool>  d,    clk_dst;
    sc_core::sc_out<bool> q;
    bool ff1 = false, ff2 = false;

    SC_CTOR(Sync2FF) { SC_METHOD(sample); sensitive << clk_dst.pos(); }
    void sample() { ff2 = ff1; ff1 = d.read(); q.write(ff2); }
};
```

## Reset Distribution

Reset is usually active-low (`rst_n`). The platform top drives it:

```cpp
sc_core::sc_signal<bool> rst_n("rst_n");

// Assert reset, run one clock cycle, deassert
rst_n.write(false);
sc_core::sc_start(20, sc_core::SC_NS);  // 1 clock cycle at 50 MHz
rst_n.write(true);
sc_core::sc_start();                    // run the rest of simulation
```

All modules that need reset receive the same `rst_n` signal — fan-out is free in SystemC signals.

## Reset Sequence Pitfalls

- **Starting simulation without reset** — peripherals have uninitialized internal state. Firmware may read garbage register values.
- **Reset too short** — if the reset pulse is shorter than the slowest peripheral's clock period, that peripheral may miss the reset edge.
- **Power-on reset vs. software reset** — some registers should not reset on software reset. Model this with two reset inputs: `por_n` (power-on) and `sw_rst_n`.

## Timing Annotations vs. Real Clocks

In LT models, modules often ignore the `clk` signal entirely and use `wait(N * cycle_time)` inside SC_THREADs:

```cpp
void uart_model::tx_thread() {
    while (true) {
        wait(baud_period);        // wait one bit period
        shift_out_bit();
    }
}
```

This avoids the overhead of a simulated clock edge for every cycle while still modeling timing at the baud-rate granularity.

## Summary Table

| Concept | LT VP approach | AT / Cycle-accurate approach |
|---|---|---|
| Clock | `sc_clock` bound but often ignored | `sc_clock` drives all edge-sensitive processes |
| Reset | Driven by `sc_main` before `sc_start` | Driven by reset controller module |
| CDC | Direct signal connection | Two-flop synchronizer |
| Timing | `wait(delay)` in SC_THREAD | `sensitive << clk.pos()` in SC_METHOD |

**Interview answer:** Clocks are modeled with `sc_clock` and distributed via `sc_in<bool>` ports. Reset is a plain `sc_signal<bool>` asserted by `sc_main` before `sc_start` runs. LT VPs often skip cycle-level clock sensitivity and instead annotate delays with `wait(N * period)`, but always model reset so firmware initialization is correct.
