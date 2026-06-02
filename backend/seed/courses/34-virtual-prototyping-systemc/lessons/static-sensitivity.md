# Static Sensitivity Lists

Static sensitivity is the set of events that trigger a process, declared *once* at elaboration time in the module constructor. Every time one of those events fires, the simulator schedules the process for re-execution. This is the primary mechanism for modeling combinational and clocked RTL logic in SystemC.

## Declaring Static Sensitivity

Sensitivity is established with the `sensitive` object inside `SC_CTOR` (or the equivalent constructor):

```cpp
SC_MODULE(GateModel) {
    sc_in<bool> a, b;
    sc_out<bool> y;

    SC_CTOR(GateModel) {
        SC_METHOD(compute);
        sensitive << a << b;    // re-run whenever a or b changes
    }

    void compute() {
        y.write(a.read() & b.read());
    }
};
```

The `<<` operator chains signals, ports, and events into the sensitivity list. The list is **static** — it cannot change after elaboration ends.

## What Can Appear in a Sensitivity List

| Source | Notation | Triggered When |
|---|---|---|
| `sc_in<T>` port | `sensitive << port` | Signal value changes |
| `sc_signal<T>` | `sensitive << sig` | Signal value changes |
| `sc_event` | `sensitive << ev` | Event is notified |
| `.pos()` | `sensitive << clk.pos()` | Rising edge |
| `.neg()` | `sensitive << clk.neg()` | Falling edge |
| `.value_changed_event()` | `sensitive << sig.value_changed_event()` | Explicit event form |

## Clocked Processes

For synchronous logic, sensitivity is typically limited to a clock edge:

```cpp
SC_MODULE(DFF) {
    sc_in_clk   clk;
    sc_in<bool> d;
    sc_out<bool> q;

    SC_CTOR(DFF) {
        SC_METHOD(latch);
        sensitive << clk.pos();    // rising edge only
    }

    void latch() {
        q.write(d.read());
    }
};
```

Using `.pos()` and `.neg()` is *more efficient* than sensitivity to the whole clock signal, because the process only wakes on the relevant edge.

## SC_CTHREAD: Implicit Sensitivity

`SC_CTHREAD` is a shorthand that creates a thread sensitive to a single clock edge and allows `wait()` calls:

```cpp
SC_MODULE(Pipeline) {
    sc_in_clk clk;

    SC_CTOR(Pipeline) {
        SC_CTHREAD(run, clk.pos());   // sensitivity built in
    }

    void run() {
        while (true) {
            wait();   // wait for next rising edge
            // ...
        }
    }
};
```

## Sensitivity to Multiple Events (OR)

All events in a static sensitivity list form an **OR** relationship — the process wakes if *any* one fires:

```cpp
SC_CTOR(Mux) {
    SC_METHOD(select);
    sensitive << sel << a << b;   // any change wakes the method
}
```

For an **AND** relationship (wake only when all events fire), dynamic sensitivity with `wait(e1 & e2)` inside an `SC_THREAD` is required — static sensitivity cannot express AND.

## Common Pitfalls

1. **Missing signals in the sensitivity list**: a combinational process that reads a signal but is not sensitive to it will produce stale outputs — a classic RTL modeling bug that mimics a latch inferred unintentionally.
2. **Sensitive to wrong edge**: being sensitive to `clk` instead of `clk.pos()` makes the process run on both edges, doubling activations.
3. **Sensitive << in SC_THREAD**: `SC_THREAD` processes use `wait()` for dynamic control; adding static sensitivity to a thread is allowed but rarely needed and can cause confusion.
4. **Modifying sensitivity after elaboration**: SystemC does not support this. Sensitivity is fixed when `sc_start()` is called.

## Worked Example: Priority Encoder

```cpp
SC_MODULE(PriorityEnc) {
    sc_in<sc_uint<4>> req;
    sc_out<sc_uint<2>> grant;
    sc_out<bool>       valid;

    SC_CTOR(PriorityEnc) {
        SC_METHOD(encode);
        sensitive << req;          // static: re-run on any req change
    }

    void encode() {
        sc_uint<4> r = req.read();
        if      (r[3]) { grant.write(3); valid.write(true); }
        else if (r[2]) { grant.write(2); valid.write(true); }
        else if (r[1]) { grant.write(1); valid.write(true); }
        else if (r[0]) { grant.write(0); valid.write(true); }
        else           { grant.write(0); valid.write(false); }
    }
};
```

> **Interview answer:** Static sensitivity is an OR list of events/signals declared in the constructor with `sensitive <<`; the process re-executes whenever any listed event fires, and the list cannot be modified after elaboration — it models how RTL combinational and clocked logic responds to input changes.
