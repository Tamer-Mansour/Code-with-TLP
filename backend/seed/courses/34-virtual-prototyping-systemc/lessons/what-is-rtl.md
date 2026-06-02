# What Is RTL?

Register-Transfer Level (RTL) is the most common abstraction used in digital hardware design. At RTL, you describe hardware as a network of registers connected by combinational logic, and every operation is tied to a clock edge.

## The RTL Mental Model

Think of RTL as a cycle-by-cycle instruction manual for hardware. At every rising (or falling) clock edge, registers either hold their value or load a new one computed by surrounding logic. The design is fully time-aware: you can pinpoint exactly which cycle each bit changes.

A simple RTL model for an adder-accumulator in SystemC looks like this:

```cpp
SC_MODULE(Accumulator) {
    sc_in<bool>       clk;
    sc_in<sc_uint<8>> data_in;
    sc_in<bool>       load;
    sc_out<sc_uint<8>> data_out;

    sc_uint<8> reg_value;

    void do_accumulate() {
        if (clk.posedge()) {
            if (load.read())
                reg_value = data_in.read();
            else
                reg_value += data_in.read();
            data_out.write(reg_value);
        }
    }

    SC_CTOR(Accumulator) {
        SC_METHOD(do_accumulate);
        sensitive << clk.pos();
    }
};
```

Every signal is explicit. Every cycle matters.

## What RTL Captures

| RTL Element | What It Represents |
|---|---|
| Registers (`sc_signal`, flip-flops) | State held between clock edges |
| Combinational blocks | Logic computed within a cycle |
| Clock sensitivity lists | Exact timing of state updates |
| Reset conditions | Hardware startup state |
| Wire widths | Bit-level data representation |

## Why RTL Exists

RTL sits directly above gate-level netlist but below behavioral C/C++. It is the standard hand-off format between logic designers and synthesis tools. Electronic Design Automation (EDA) tools synthesize RTL into a gate-level netlist that maps directly to silicon or FPGA fabric.

The key properties of RTL:

- **Cycle-accurate** — the simulation matches real hardware clock-by-clock.
- **Bit-accurate** — signal widths match exactly what goes on the wires.
- **Synthesizable** — EDA tools can convert RTL into actual gates.
- **Timing-detailed** — setup/hold violations and propagation delays can be analyzed.

## Common RTL Pitfalls

1. **Forgetting the clock edge** — reading a signal combinationally when you meant to sample it on a clock edge leads to race conditions.
2. **Latches from incomplete if-else** — in RTL, every signal must have a defined value in every branch; otherwise synthesis infers an unwanted latch.
3. **Blocking vs. non-blocking assignment confusion** — mixing the two in SystemVerilog (or SystemC equivalent) causes hard-to-find simulation mismatches.
4. **Slow simulation** — because every signal toggle is an event, RTL simulations are inherently slow for large designs.

## RTL in the Wider Design Flow

```
Algorithm → Behavioral → RTL → Gate-Level → Layout
                          ↑
               (You are here: synthesis starts here)
```

RTL is the entry point for synthesis. Everything above it (behavioral, algorithmic) is faster to simulate but not directly synthesizable without extra steps. Everything below it (gate-level, layout) is more detailed but far slower to simulate and nearly impossible to write by hand for large designs.

## Interview Answer

> "RTL models hardware as registers updated on clock edges connected by combinational logic. It is cycle-accurate and bit-accurate, making it synthesizable but slow to simulate because every signal transition is tracked."
