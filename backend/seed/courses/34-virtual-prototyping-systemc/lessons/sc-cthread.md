# SC_CTHREAD and Clocked Threads

`SC_CTHREAD` (clocked thread) is a specialised variant of `SC_THREAD` with a **single, fixed clock edge** as its only trigger. It was introduced primarily for High-Level Synthesis (HLS) tools, which need to know exactly when a process samples its inputs.

## Syntax

```cpp
SC_MODULE(Accumulator) {
    sc_in<bool>        clk;
    sc_in<bool>        rst;
    sc_in<sc_int<16>>  data_in;
    sc_out<sc_int<32>> accum;

    SC_CTOR(Accumulator) {
        SC_CTHREAD(run, clk.pos());   // tied to positive edge of clk
        reset_signal_is(rst, true);   // active-high synchronous reset
    }

    void run();
};
```

`SC_CTHREAD(func, edge)` — the second argument is the **clock event** and cannot be changed at runtime. There is no `sensitive <<` for clocked threads; the clock is their only sensitivity.

## Reset Handling

Two helper calls work with `SC_CTHREAD`:

```cpp
reset_signal_is(rst, true);     // synchronous reset, active high
async_reset_signal_is(rst, true); // asynchronous reset, active high
```

Inside the thread body the idiom is:

```cpp
void Accumulator::run() {
    // Initialisation code — runs on every reset
    accum.write(0);
    wait();                // wait for first clock edge after reset

    while (true) {
        accum.write(accum.read() + data_in.read());
        wait();
    }
}
```

When reset is asserted, the thread restarts from the top — the lines before `wait()` are the reset logic.

## wait() Inside SC_CTHREAD

Inside an `SC_CTHREAD`, `wait()` always means "wait for the **next clock edge**". There is no other form — you cannot wait on arbitrary events or timeouts. This constraint makes the behaviour fully cycle-accurate and directly synthesisable.

```cpp
// Legal
wait();         // next rising edge (if clk.pos() was used)
wait(3);        // three clock edges

// Illegal inside SC_CTHREAD
wait(10, SC_NS);                    // compile/runtime error
wait(some_signal.value_changed_event());   // error
```

## Comparison: SC_THREAD vs SC_CTHREAD

| Feature | SC_THREAD | SC_CTHREAD |
|---|---|---|
| Sensitivity | Any event(s), changeable with `wait(event)` | Fixed single clock edge |
| `wait()` forms | All forms legal | Only `wait()` and `wait(N)` |
| Reset support | Manual | Built-in (`reset_signal_is`) |
| Target use case | Untimed / loosely timed TLM models | Cycle-accurate RTL / HLS |
| Synthesisable | No (without HLS) | Yes (Catapult, Stratus, etc.) |

## HLS Use Case

HLS tools such as Cadence Stratus and Mentor Catapult read `SC_CTHREAD` modules and synthesise RTL. The tool maps each `wait()` to one clock cycle of latency. Developers describe the algorithm at a high level:

```cpp
void fir_filter() {
    // reset
    y.write(0);
    wait();

    while (true) {
        sc_int<32> result = 0;
        for (int i = 0; i < TAPS; i++) {
            result += coeff[i] * delay_line[i];
        }
        delay_line[TAPS-1] = x.read();
        // shift delay line
        for (int i = 0; i < TAPS-1; i++)
            delay_line[i] = delay_line[i+1];
        y.write(result >> FRAC_BITS);
        wait();   // one cycle per output sample
    }
}
```

The HLS tool decides how to pipeline or unroll the loops to meet timing.

## When SC_CTHREAD is Used Outside HLS

Even without a synthesis tool, `SC_CTHREAD` is useful when:

- You need guaranteed reset behaviour without writing it manually.
- You want to prevent accidental use of non-cycle-aligned `wait()` calls.
- Your simulation must be strictly cycle-accurate (no sub-cycle events).

## Common Pitfall: Confusing with SC_THREAD

Developers sometimes write `SC_THREAD` when they mean `SC_CTHREAD` in an HLS project. The simulation will run, but the synthesis tool will reject the module because it finds `wait(event)` calls that it cannot map to a fixed latency.

> **Interview answer:** `SC_CTHREAD` is a clock-bound variant of `SC_THREAD` whose only trigger is a fixed clock edge and whose only legal `wait()` forms are `wait()` and `wait(N)`. It is the standard process type for High-Level Synthesis targets because its strictly cycle-aligned semantics can be directly mapped to synchronous RTL flip-flop behaviour.
