# SRAM vs DRAM: How They Differ

SRAM (Static RAM) and DRAM (Dynamic RAM) are the two dominant semiconductor memory technologies in modern computers. They differ fundamentally in how they store a bit, and those differences cascade into everything from access speed to power consumption to cost per bit.

## How SRAM Stores a Bit

SRAM uses a **bistable latch** — typically six transistors (6T cell) — to hold one bit. The circuit stays in its state indefinitely as long as power is supplied; there is no charge to drain and no need for refresh.

```
     VDD
      |
   M1   M2   (load transistors)
      |
 Q ---+--- Q̄   (two cross-coupled inverters form the latch)
      |
   M3   M4   (drive transistors)
      |
   M5   M6   (access transistors — controlled by word line)
      |
  BL       BL̄  (bit lines)
```

**Key properties:**
- Access time: 1–10 ns (on-die L1/L2) to ~30 ns (discrete SRAM chips)
- No refresh required
- 6 transistors per bit → low density, high cost per bit
- High power in standby (leakage current through all those transistors)
- Used for: CPU registers, L1/L2/L3 caches, TLBs, branch predictor tables

## How DRAM Stores a Bit

DRAM uses a **capacitor and one transistor** (1T1C cell) per bit. The capacitor is either charged (logic 1) or discharged (logic 0), but capacitors leak charge over time, so DRAM must be **refreshed** approximately every 64 milliseconds.

```
     Word Line
         |
      [Transistor]
         |
     [Capacitor]   ← charge = 1, no charge = 0
         |
      Bit Line
```

Reading DRAM is **destructive**: the read operation discharges the capacitor to sense the bit, and the controller must immediately write the value back. This is called a **read-modify-write** cycle.

**Key properties:**
- Access time: 60–100 ns (random access latency)
- Refresh required every ~64 ms (consumes ~15% of bandwidth)
- 1 transistor + 1 capacitor per bit → very high density, low cost per bit
- Higher burst bandwidth than SRAM for sequential access (DDR protocols)
- Used for: main memory (RAM sticks), GPU frame buffers, last-level caches on some SoCs

## Side-by-Side Comparison

| Property | SRAM | DRAM |
|----------|------|------|
| Cell structure | 6 transistors | 1 transistor + 1 capacitor |
| Bit density | Low | High |
| Cost per bit | High (~10–30×) | Low |
| Access latency | 1–10 ns | 60–100 ns |
| Refresh needed | No | Yes (~64 ms) |
| Read destructive | No | Yes |
| Power (active) | Low | Low |
| Power (standby) | High (leakage) | Low |
| Typical use | Cache, registers | Main memory |

## Why DRAM Has High Latency

DRAM is organized into **rows and columns** (a 2D array). Accessing a cell requires:

1. **Row Activate (RAS):** Open the selected row — all capacitors in that row discharge onto bit lines (~30–40 ns)
2. **Column Read (CAS):** Latch the selected column's bit line (~10–20 ns)
3. **Precharge:** Reset bit lines for the next access (~10–20 ns)

The RAS-to-CAS delay (`tRCD`) plus CAS latency (`CL`) plus precharge (`tRP`) sum to the full random-access latency. Successive accesses to the **same open row** are much faster (hit the row buffer) — this is **spatial locality** at the DRAM level.

## DRAM Row Buffer Behavior

```
First access to row 42:   RAS + CAS = 70 ns (row buffer miss)
Second access to row 42:  CAS only  = 15 ns (row buffer hit)
Access to row 43:         Precharge + RAS + CAS = 90 ns (row conflict)
```

Sequential access patterns that stay within one DRAM row achieve much higher effective bandwidth than random row-switching patterns.

## Worked Example

A system has 32 KB of L1 SRAM cache and 16 GB of DRAM.

- Cost ratio: SRAM ~$10/MB, DRAM ~$0.003/MB (at typical market prices, approximately 3000× cheaper per bit for DRAM)
- If the entire 16 GB were SRAM: 16 × 1024 MB × $10/MB = **$163,840**
- Actual DRAM cost: 16 GB × $0.003/MB × 1024 MB/GB ≈ **$49**

This is why only a tiny fraction of total memory capacity is SRAM — it would be prohibitively expensive to build a large SRAM main memory.

## Common Pitfalls

- **Conflating SRAM cache with "fast RAM"**: DDR4 RAM is DRAM, not SRAM. Adding more RAM sticks does not make cache faster.
- **Ignoring refresh overhead**: Under heavy access, DRAM refresh can cause periodic latency spikes (refresh interferes with normal row access for ~7 µs per bank per 64 ms window).
- **Assuming all DRAM is the same**: LPDDR (mobile), DDR4/5 (desktop), HBM (GPU/AI) are all DRAM variants with very different bandwidth, latency, and power profiles.

> **Interview answer:** SRAM uses six transistors per bit for a stable latch — fast but expensive and area-hungry, so it is used for caches. DRAM uses one transistor and one capacitor per bit — dense and cheap but slow and requires periodic refresh, so it is used for main memory.
