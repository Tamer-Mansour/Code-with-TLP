# RTL vs TLM: The Core Differences

RTL and TLM are not competing alternatives — they are tools for different jobs. Understanding where each fits in the design flow prevents you from reaching for the wrong abstraction at the wrong moment.

## Side-by-Side Comparison

| Dimension | RTL | TLM |
|---|---|---|
| Unit of communication | Signal transition (1 bit, 1 cycle) | Transaction (logical operation) |
| Time representation | Exact clock cycles | Annotated delay, quantum-based |
| Bit accuracy | Full — every wire width matches silicon | Functional — data is correct, wires hidden |
| Simulation speed | Slow (millions of events per ms) | Fast (10x–1000x faster than RTL) |
| Synthesizability | Yes (EDA tools convert to gates) | No (too abstract) |
| Primary use | Pre-silicon verification, sign-off | Virtual prototyping, SW bring-up |
| Typical language | VHDL, Verilog, SystemVerilog, SystemC RTL | SystemC + TLM-2.0 API |
| Who writes it | Hardware engineers | Architects, platform engineers |

## The Fundamental Trade-off

RTL captures hardware truth with precision. Every wire, every flip-flop, every gate delay is accounted for. But that precision has a cost: simulation must process millions of signal events per millisecond of simulated time.

TLM discards those details on purpose. A memory read that takes 10 clock cycles in RTL becomes a single `b_transport()` call with a 10 ns `sc_time` annotation in TLM. The simulator processes one event instead of tens of thousands.

```cpp
// RTL approach — 10 cycles of signal toggling (pseudocode)
addr_bus.write(0x2000);
req.write(true);
wait(clk.posedge_event());
while (!ack.read()) wait(clk.posedge_event());
data = data_bus.read();
req.write(false);

// TLM approach — one function call
trans.set_address(0x2000);
socket->b_transport(trans, delay);  // delay = annotated 10 ns
data = *reinterpret_cast<uint32_t*>(trans.get_data_ptr());
```

Both produce the same `data` value. Only RTL tells you what happened on the wires in between.

## Accuracy vs. Speed: Not a Binary Choice

Neither RTL nor TLM is "accurate" or "fast" in absolute terms. Accuracy and speed are both relative to what you need to know.

- **RTL is accurate for timing** — you can run static timing analysis and find setup/hold violations.
- **TLM is accurate for function** — the software sees the right data at the right address; it just does not see every bus cycle.
- **TLM with annotated delays is accurate for performance trends** — you can spot bandwidth bottlenecks and latency hotspots without full RTL.

## Which Stage Uses Which

```
Design Phase          Abstraction       Primary Goal
─────────────────────────────────────────────────────
Architecture          TLM (LT)          Feasibility
SW Platform           TLM (LT/AT)       Driver development
Performance           TLM (AT)          Bandwidth/latency
RTL Implementation    RTL               Correct hardware
Verification          RTL + Formal      Functional sign-off
Physical Design       Gate / Layout     Timing closure
```

## Mixed-Level Simulation

In practice, teams run both levels together. A TLM model of the CPU subsystem drives RTL under test via a transactor — an adapter that converts TLM transactions into pin-wiggling sequences. This is called a hybrid or mixed-level simulation.

```
[TLM CPU Model] ──transactor──> [RTL DMA] ──> [TLM Memory Model]
```

The transactor absorbs the mismatch between abstraction levels. The RTL block gets realistic stimulus without requiring the entire system to be RTL.

## Common Misconception

> "TLM is just a shortcut for lazy designers."

No. TLM enables work that RTL physically cannot support: running a full Linux boot in minutes instead of weeks. At RTL simulation speeds, a 1-second Linux boot would take months of wall-clock simulation time. TLM makes system-level software validation possible at all.

## Interview Answer

> "RTL tracks every signal transition on every clock cycle, making it cycle-accurate and synthesizable but slow. TLM replaces bus transactions with function calls and annotated delays, making simulation 10x–1000x faster at the cost of hiding wire-level detail. They serve different phases of the design flow and are often used together via transactors."
