# Snooping vs Directory-Based Coherence

Cache coherence requires that every cache be notified when a shared line is written. How that notification is delivered determines whether the coherence mechanism can scale to tens or thousands of processors.

## Snooping Coherence

In a **snooping** protocol, every cache controller monitors (snoops) a shared broadcast medium — historically a bus, today often a ring or crossbar interconnect. When any core issues a coherence transaction, every other core receives it automatically.

### How It Works

```
Core 0     Core 1     Core 2     Core 3
  |           |          |          |
  +-----+-----+----------+----------+
                 Shared Bus
```

1. Core 0 wants to write address `A`.
2. Core 0 broadcasts **BusRdX(A)** on the bus.
3. Every cache controller snoops the bus, sees the transaction, and invalidates any copy of `A`.
4. Core 0 is now the sole owner; it transitions to **Modified** state.

### Strengths

- Simple to implement — no centralized state to maintain.
- Low latency for small core counts (2–16 cores) — the broadcast arrives at all caches simultaneously.
- Cache-to-cache transfer is possible: the owner can supply data directly without a main-memory round-trip.

### Weaknesses

- **Does not scale**: broadcast traffic grows as O(N) per transaction. With 64 cores, every write floods 63 other controllers. Bus bandwidth becomes the bottleneck.
- A shared electrical bus is physically limited to ~16–32 processors before signal integrity fails.
- Ring interconnects (Intel Core, Xeon) partially mitigate this but still have O(N) hop counts.

### Modern Snooping Variants

Intel's **ring bus** (used in Sandy Bridge through Skylake-X) sends snoop filters to reduce broadcasts. AMD's **Infinity Fabric** uses a mesh but still employs snooping within a single die. These are "snoop-based with filters" rather than pure broadcast.

## Directory-Based Coherence

A **directory** is a data structure that explicitly records which caches hold each memory block. Instead of broadcasting, the memory controller sends targeted messages only to the caches that have a copy.

### Directory Structure

Each memory block has a directory entry:

```
Address | State | Sharer Bitfield (1 bit per processor)
--------|-------|--------------------------------------
0x1000  |  S    | 1 1 0 0 1 0 0 0   (P0, P1, P4 share it)
0x2000  |  M    | 0 0 1 0 0 0 0 0   (P2 owns it, dirty)
0x3000  |  I    | 0 0 0 0 0 0 0 0   (no one has it)
```

### Write Operation with Directory

```
Core 2 wants to write 0x1000 (currently Shared by P0, P1, P4):

1. Core 2 → Directory: "Write request for 0x1000"
2. Directory → Core 0: "Invalidate 0x1000"
3. Directory → Core 1: "Invalidate 0x1000"
4. Directory → Core 4: "Invalidate 0x1000"
5. P0, P1, P4 send ACKs to Directory (or directly to Core 2)
6. Directory → Core 2: "You may write; all invalidated"
7. Core 2 updates state to Modified; directory records {M, Core 2}
```

This is **point-to-point** messaging — no broadcast, just targeted invalidations.

### Strengths

- **Scales to hundreds or thousands of processors** — traffic is proportional to actual sharers, not total cores.
- No shared bus required — works over any network topology (mesh, torus, fat-tree).
- Foundation of all large-scale systems: SGI Origin, IBM Blue Gene, AMD EPYC multi-socket, ARM CCI/CMN.

### Weaknesses

- **Higher latency**: a write requires at minimum two round-trips (request + ACK) vs. one broadcast.
- Directory storage overhead: with N processors, each entry needs log₂(N) bits (full bit-vector) or more complex structures for very large N.
- Directory itself can become a hot spot if many caches request the same address.

## Scalability Comparison

| Property | Snooping | Directory |
|---|---|---|
| Message complexity | O(N) per transaction | O(k) where k = sharers |
| Latency (small N) | Lower | Higher |
| Latency (large N) | Unbounded | Bounded |
| Hardware complexity | Low | Moderate-High |
| Max practical scale | ~64 cores | Thousands of nodes |
| Used in | Desktop/laptop CPUs | Servers, HPC, CXL |

## Hybrid Approaches

Real systems blend both strategies:

- **Intel Xeon (multi-socket):** Snooping within a socket (via ring bus), directory-based across sockets (via QPI/UPI).
- **AMD EPYC:** Snooping within a chiplet, directory-based across chiplets and sockets via Infinity Fabric.
- **Snoop filters**: A small cache that tracks which remote caches hold each line, reducing unnecessary broadcasts in snooping systems.

## CXL (Compute Express Link) and Beyond

The emerging **CXL** standard defines a coherence protocol for attaching accelerators and memory expanders to CPUs. It uses a directory-based approach over PCIe physical links, enabling cache-coherent access between CPUs and GPUs or disaggregated memory — effectively extending the coherence domain off the CPU die.

## Interview Answer

> "Snooping coherence broadcasts every memory transaction on a shared bus so all caches can react simultaneously — it is simple and fast for small core counts but doesn't scale because bus traffic grows linearly with core count. Directory-based coherence maintains an explicit table of which caches hold each block and sends targeted invalidations only to those caches, making it O(sharers) rather than O(all cores) — the standard approach for large servers and HPC systems at the cost of added latency and directory storage overhead."
