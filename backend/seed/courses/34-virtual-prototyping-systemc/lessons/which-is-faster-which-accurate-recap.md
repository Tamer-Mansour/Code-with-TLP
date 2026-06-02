# Which Is Faster, Which Is More Accurate, and Why

Speed and accuracy are in direct tension across the four major representation levels of a digital design. Every experienced embedded or SoC engineer must articulate this trade-off instantly in an interview.

## The Four Levels at a Glance

| Level | Typical speed | Accuracy | Primary use |
|-------|--------------|----------|-------------|
| **Functional ISS / Untimed VP** | 100 MIPS–1 GIPS | Instruction result only | SW bring-up, OS boot |
| **Approximately-timed TLM VP** | 1–100 MIPS | Rough timing (±10–30 %) | HW/SW co-design, perf. estimation |
| **Cycle-accurate C++ model** | 1–10 MIPS | Exact cycle counts | Microarchitecture exploration |
| **RTL simulation** | 0.001–1 MIPS | Bit-exact, gate behavior | Design verification, signoff |

"MIPS" here means simulated instructions per second of wall-clock time, not the target ISA.

## Why Functional Models Are Fastest

A functional ISS like QEMU or gem5 in SE mode executes one basic block at a time, JIT-compiling guest instructions to host instructions. There is no time model at all — the host advances a program-counter register and performs register file updates. No stall logic, no latch propagation, no event queue processing.

```cpp
// Pseudocode: pure functional decode-execute
while (running) {
    uint32_t insn = mem_read32(pc);
    pc += 4;
    decode_and_execute(insn, regs);  // no time, no stalls
}
```

This allows several hundred million to several billion instructions per second on modern hardware.

## Why TLM VPs Are Slower Than Functional but Faster Than RTL

An approximately-timed TLM VP runs a SystemC event-driven kernel. Every `wait()` call processes the event queue, context-switches between processes, and updates simulation time. The overhead is real but bounded — typically a few microseconds of wall-clock time per simulated transaction. Crucially, bus transactions are modelled as single function calls, not as hundreds of clock-edge events.

```cpp
// AT initiator: one payload, one blocking call — no per-cycle events
tlm::tlm_generic_payload gp;
gp.set_address(addr);
gp.set_data_ptr(buf);
gp.set_data_length(4);
sc_time delay = SC_ZERO_TIME;
socket->b_transport(gp, delay);   // collapses the entire transfer
```

Compare this to RTL, where a 4-beat AXI burst fires 4 × (4 edges per beat) = 16 distinct simulation events just for the data phase.

## Why RTL Is Slowest

RTL simulation evaluates every signal at every clock edge. For a 100 MHz SoC with 10 million gates, each simulated microsecond triggers ~10 million signal evaluations. Even optimized event-driven simulators (VCS, Xcelium) can sustain only a few hundred kilohertz of simulated clock on commodity hardware. Gate-level simulation is another 10–100× slower still.

## Why RTL Is Most Accurate

RTL captures:
- **Bit-exact arithmetic** including overflow, carry, saturation
- **Timing hazards** (setup/hold violations with SDF back-annotation)
- **Reset and power-on behavior** cycle by cycle
- **Corner-case hardware bugs** such as pipeline stalls under back-pressure

Functional models skip all of these. TLM models approximate some (approximate timing, no bit-level hazards).

## The Practical Design Point

```
Goal                        Choose
─────────────────────────────────────────────────
Boot Linux ASAP             Functional ISS / QEMU
HW/SW co-design + perf      AT-TLM VP
Microarch tuning            Cycle-accurate model
Bug-free RTL for tapeout    RTL + formal + DV
```

## Common Interview Pitfall

Candidates often say "VPs are faster because they skip RTL detail." That is true but incomplete. The fuller answer mentions **why** detail is skipped (event granularity, latch propagation) and **what is lost** (bit hazards, cycle-exact stalls, power/timing accuracy).

## Interview Answer

> "Functional ISS runs fastest (1 GIPS) because there is no time model — just register updates. AT-TLM VPs are 10–1000× faster than RTL because transactions collapse hundreds of clock-edge events into one function call. RTL is slowest but bit-exact: it captures every signal at every edge, which is essential for signoff and DV. The right level depends on what question you are answering."
