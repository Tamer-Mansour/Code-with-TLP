# Latches, Flip-Flops, and Registers

This lesson examines the storage elements that give digital systems the ability to remember state — from the humble SR latch to the D flip-flop used in every CPU register and cache cell.

## The SR Latch — Storage from Feedback

The SR (Set/Reset) latch is the most primitive memory cell. Built from two cross-coupled NOR gates:

```
         S ──────────NOR─────── Q
                   ↑         ↓
         R ──────────NOR─────── Q'
```

**NOR-based SR truth table:**

```
S | R | Q(next) | Q'(next) | State
1 | 0 |    1    |     0    | Set (force Q=1)
0 | 1 |    0    |     1    | Reset (force Q=0)
0 | 0 |  Q_prev |  Q'_prev | Hold (stable memory)
1 | 1 |    0    |     0    | Forbidden (contradicts Q ≠ Q')
```

**Why does S=0, R=0 hold the previous value?**

Trace through: if Q=1 and Q'=0, then NOR(R=0, Q'=0) = NOR(0,0) = 1 = Q (stable). NOR(S=0, Q=1) = NOR(0,1) = 0 = Q' (stable). The latch is self-reinforcing.

**NAND-based SR latch** uses active-LOW inputs — asserting S_bar=0 sets Q=1. Commonly drawn with bubbles on the inputs to indicate active-LOW. The forbidden state is both inputs simultaneously LOW.

## The D Latch — Eliminating the Forbidden State

The D (Data) latch solves the forbidden state by deriving S and R from a single data input:

```
S = D AND Enable
R = D' AND Enable
```

This ensures S and R can never both be 1 simultaneously.

**D latch truth table:**

```
D | Enable | Q(next) | Behavior
0 |   1    |    0    | Transparent — Q follows D
1 |   1    |    1    | Transparent — Q follows D
X |   0    |  Q_prev | Opaque — Q holds last value
```

Schematic (gate level):

```
D ──┬──AND── S ──┐
    │              SR-NOR ── Q
    NOT──AND── R ──┘
           ↑
         Enable
```

The D latch is **level-sensitive**: it is transparent (Q = D) for the entire duration that Enable is HIGH. Any noise or glitch on D while Enable is HIGH propagates directly to Q — a serious reliability concern in real circuits.

## The Edge-Triggered D Flip-Flop

The **D flip-flop (DFF)** eliminates the level-sensitivity problem. It captures D only at the **rising (or falling) clock edge** and ignores D at all other times.

### Master-Slave Implementation

Two D latches chained with inverted enables:

```
        D ──[D-Latch (Master)]── M ──[D-Latch (Slave)]── Q
                  ↑                           ↑
                CLK'                          CLK
```

- When CLK=0: Master is transparent (M = D), Slave is opaque (Q holds).
- When CLK=1: Master is opaque (M holds D captured at the edge), Slave is transparent (Q = M).
- At the rising edge (0→1): Master closes (captures D), then Slave opens (Q ← M). This transfer happens atomically at the edge.

**Timing diagram:**

```
CLK:   ____↑‾‾‾‾↓____↑‾‾‾‾↓____
D:     ___XXXXX‾‾‾‾‾‾XXXXX____
       (setup violation)  ↑setup window
M:     _________‾‾‾‾‾‾‾‾‾____   (captured at rising edge)
Q:               ________‾‾‾‾‾‾‾____  (Q updates after propagation delay)
                 ↑ t_pcq after edge
```

### Setup Time, Hold Time, and Clock-to-Q

These three parameters define the flip-flop's timing constraints precisely:

| Parameter | Symbol | Meaning | Typical CMOS value |
|-----------|--------|---------|-------------------|
| Setup time | t_su | D must be stable before the rising edge | 50–200 ps |
| Hold time | t_h | D must remain stable after the rising edge | 10–50 ps |
| Clock-to-Q | t_pcq | Q becomes valid this long after the rising edge | 100–300 ps |

**Timing constraint on combinational logic between two flip-flops:**

```
t_comb ≤ T_clock − t_pcq − t_su

Example: T = 500 ps (2 GHz), t_pcq = 150 ps, t_su = 100 ps
→ t_comb ≤ 250 ps (max combinational delay per stage)
```

If this constraint is violated, the circuit will occasionally produce wrong results — this is a **setup time violation**.

**Hold time violation** is the opposite: D changes too quickly after the clock edge. This can happen when combinational logic is extremely fast (zero gates), forcing design teams to add buffer delays.

## T Flip-Flop and JK Flip-Flop

### T (Toggle) Flip-Flop

```
Input: T (Toggle)
Behavior:
  T = 0 → Q holds (no change)
  T = 1 → Q toggles (Q_next = NOT Q)
```

Implementation: `D = T XOR Q`

Used in binary counters. A chain of T flip-flops with T=1 creates a ripple counter — each flip-flop divides the clock by 2.

**4-bit ripple counter timing diagram:**

```
CLK: ↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑_↑
Q0:  _‾_‾_‾_‾_‾_‾_‾_‾  (÷2)
Q1:  ___‾‾___‾‾___‾‾__  (÷4)
Q2:  _______‾‾‾‾______  (÷8)
Q3:  _______________‾‾  (÷16)
```

### JK Flip-Flop

Generalizes SR: J=Set, K=Reset, J=K=1 → Toggle. No forbidden state.

```
J | K | Q(next)
0 | 0 | Q       (hold)
0 | 1 | 0       (reset)
1 | 0 | 1       (set)
1 | 1 | NOT Q   (toggle)
```

The JK flip-flop is universal — any other flip-flop type can be derived from it.

## Registers in the CPU

### N-bit Register

An N-bit register is N D flip-flops sharing a clock and write-enable signal:

```
For bit i:
  D_ff_input[i] = WE ? D_in[i] : Q[i]
  Q[i] is updated on the next rising clock edge
```

Write enable prevents accidental overwrites: the register file can update only the selected destination register, leaving all others unchanged.

### The RISC-V Register File (32 × 32-bit)

```
Interface:
  Read 1: rs1[4:0] → regfile_data1[31:0]   (combinational, same cycle)
  Read 2: rs2[4:0] → regfile_data2[31:0]   (combinational, same cycle)
  Write:  rd[4:0], wr_data[31:0], RegWrite  (latched on rising edge)

Area: 32 × 32 = 1024 flip-flops (1024 master-slave DFF pairs = ~6000 transistors)
```

In modern CPUs, the "register file" has been expanded to a much larger **physical register file** (e.g., 168 entries in Intel Skylake) to support out-of-order execution and register renaming.

### Pipeline Registers

Every stage boundary in a pipelined CPU is a set of pipeline registers:

```
IF/ID   — holds: PC+4, instruction [31:0]
ID/EX   — holds: PC+4, rs1 data, rs2 data, sign-extended immediate, rd, control signals
EX/MEM  — holds: ALU result, zero flag, rs2 data (for stores), rd
MEM/WB  — holds: memory read data OR ALU result, rd
```

On each clock edge, all values advance one register to the right. This is what enables 5 instructions to overlap in flight simultaneously.

## From Flip-Flops to Cache Memory

**SRAM (Static RAM)** — used in caches — stores each bit in a cross-coupled inverter pair (6 transistors per cell), which is essentially an SR latch with access transistors. SRAM retains data as long as power is applied and does not need refreshing.

**DRAM (Dynamic RAM)** — used in main memory — stores each bit in a single capacitor + access transistor (1 transistor per cell). The capacitor charge leaks and must be refreshed every ~64 ms. This is why DRAM is denser but slower than SRAM.

```
Memory type comparison:
 L1 SRAM:  6T/bit, ~0.5 fJ read energy, ~1 ns access, 32–64 KB capacity
 DRAM:     1T/bit, ~10 fJ read energy, ~60 ns access, 8–128 GB capacity
```

Understanding flip-flops and latches is therefore the direct foundation for understanding why L1 cache is fast (SRAM cells are large but always ready) and why main memory is slow (DRAM cells must be charged, decoded, and amplified before the data is accessible).
