# Ripple-Carry vs Carry-Lookahead Adders

Chaining full adders works, but there is a critical performance problem: each bit position must wait for the carry-out of the previous position before it can compute its own sum. This is the **carry propagation delay** — the nemesis of fast addition circuits.

## The Ripple-Carry Adder (RCA)

In a ripple-carry adder, the carry "ripples" from bit 0 to bit N-1 one stage at a time. Each full adder has a gate delay of roughly 2 gate levels for the carry path. For a 32-bit adder that is up to 64 gate delays end-to-end.

```
Delay formula (simplified):
  t_RCA = N × t_FA_carry
  For N=32, t_FA_carry ≈ 2 gates → ~64 gate delays
```

**Advantages of RCA:**
- Extremely simple to design and reason about
- Minimal gate count — just N full adders
- Fine for narrow widths (4-bit, 8-bit) or low-speed designs

**Disadvantages:**
- Latency grows linearly with bit width — unusable for 64-bit at GHz clock rates
- The critical path is the carry chain through all N stages

## Generate and Propagate Signals

The carry-lookahead adder (CLA) is built on two key per-bit signals:

| Signal | Formula | Meaning |
|--------|---------|---------|
| **Generate** G_i | A_i AND B_i | Bit i produces a carry regardless of carry-in |
| **Propagate** P_i | A_i XOR B_i | Bit i passes a carry-in through to carry-out |

With these two signals, the carry-out of bit i can be expressed without waiting for the carry-out of bit i-1:

```
C_1 = G_0 + P_0·C_0
C_2 = G_1 + P_1·G_0 + P_1·P_0·C_0
C_3 = G_2 + P_2·G_1 + P_2·P_1·G_0 + P_2·P_1·P_0·C_0
C_4 = G_3 + P_3·G_2 + P_3·P_2·G_1 + P_3·P_2·P_1·G_0 + P_3·P_2·P_1·P_0·C_0
```

Every carry is now computed from the **original inputs** A and B, not from intermediate carry results. All four carry signals can be produced simultaneously in a constant number of gate levels — typically 2 for G/P, then 2 more for the carry logic = 4 gate levels regardless of width.

## Carry-Lookahead Adder (CLA)

A 4-bit CLA block computes C_1 through C_4 in parallel, then all four sums are computed simultaneously:

```
S_i = P_i XOR C_i
```

The total delay for a 4-bit CLA is about 4-5 gate delays — versus 8 for a 4-bit RCA.

For 32-bit addition, build a **hierarchical (two-level) CLA**:

```
Level 1: Eight 4-bit CLA blocks
          Each produces a group-generate (GG) and group-propagate (GP)
Level 2: One 8-input lookahead unit over the eight groups
          Computes the carry into each group in parallel
```

A two-level 32-bit CLA runs in approximately 10-12 gate delays vs. 64 for the ripple-carry version.

## Comparison Table

| Property | Ripple-Carry Adder | Carry-Lookahead Adder |
|----------|-------------------|----------------------|
| Delay | O(N) — linear | O(log N) — logarithmic |
| Gate count | N full adders (low) | N full adders + lookahead logic (higher) |
| Wiring complexity | Very simple | More complex, more wires |
| Typical use | 4-bit / educational | 32-bit, 64-bit ALUs |
| Area | Small | Larger |

## What Real CPUs Use

Modern processors use variants of CLA, **prefix adders** (Kogge-Stone, Brent-Kung, Han-Carlson), and **carry-select adders** to push addition into a single clock cycle at multi-GHz frequencies.

- **Carry-select adder**: pre-computes two copies of each group (one assuming Cin=0, one assuming Cin=1), then uses a multiplexer to select the correct result once the carry is known.
- **Kogge-Stone**: fully parallel prefix tree — O(log N) depth, O(N log N) gates, used in Intel/AMD CPUs.

```c
// Conceptual C model of generate/propagate
uint32_t a = 0xABCD1234, b = 0x12345678;
uint32_t g = a & b;   // generate
uint32_t p = a ^ b;   // propagate
// Real CLA hardware uses these to pre-compute all carries
```

## Common Pitfalls

- Confusing **propagate** (XOR) with the sum bit — they look the same formula but serve different roles.
- A CLA still requires full adder sum stages; the lookahead only replaces the carry-chain, not the sum computation.
- Group generate/propagate at the second level use AND/OR, not XOR — a common exam mistake.

> **Interview answer:** A ripple-carry adder has O(N) delay because carries propagate serially; a carry-lookahead adder reduces this to O(log N) by computing carries in parallel from generate (A AND B) and propagate (A XOR B) signals derived directly from the input bits.
