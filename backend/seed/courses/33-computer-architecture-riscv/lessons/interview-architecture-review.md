# Interview Review: Core Architecture Concepts

This lesson is a structured rapid-review of the computer architecture concepts that appear most frequently in technical interviews at semiconductor companies, system software roles, and CPU architecture positions. Each topic includes a crisp answer you can adapt.

## 1. Von Neumann vs. Harvard Architecture

**Von Neumann**: instructions and data share the same memory bus. Simple to implement; the bottleneck is the shared bus (von Neumann bottleneck).

**Harvard**: separate instruction and data buses allow simultaneous fetch and data access. Used in embedded MCUs (AVR, PIC) and in modern CPU caches (split I-cache / D-cache).

> **Interview answer:** "Von Neumann uses a single unified memory bus; Harvard uses separate instruction and data memories. Modern CPUs implement a modified Harvard architecture at the cache level while maintaining a unified main memory."

## 2. The Five Stages of the Classic Pipeline

| Stage | Action |
|---|---|
| IF (Instruction Fetch) | Read instruction from I-cache at PC |
| ID (Instruction Decode) | Read registers, decode fields, compute immediates |
| EX (Execute) | ALU operation or branch resolution |
| MEM (Memory Access) | Load from or store to D-cache |
| WB (Write-Back) | Write result to register file |

CPI with no hazards = 1. Throughput = IPC × clock frequency.

## 3. Pipeline Hazards

**Structural**: two instructions need the same hardware resource simultaneously. Solution: stall or duplicate the resource.

**Data (RAW — read-after-write)**: instruction B needs a result that instruction A has not yet written. Solutions: forwarding/bypassing (routes result directly from EX/MEM output to EX input), or stalling.

**Control**: the next PC is not known until a branch resolves in EX. Solutions: branch prediction, delayed branch, flushing.

> **Interview answer:** "The three hazard types are structural, data, and control. Data hazards are handled by forwarding — routing the computed result directly to the input of the dependent instruction — and stalling when forwarding is impossible (e.g., load-use hazard)."

## 4. Amdahl's Law

$$S = \frac{1}{(1 - p) + \frac{p}{n}}$$

Where p = fraction of work that is parallelisable and n = number of processors. The sequential fraction (1-p) is the hard limit on speedup.

> **Interview answer:** "Amdahl's Law says speedup is bounded by the serial fraction. Even with infinite cores, a program that is 20% serial can only be 5× faster."

## 5. Cache Hierarchy — Key Numbers

| Level | Typical size | Access latency |
|---|---|---|
| L1 (split I/D) | 32–64 KB | 4–5 cycles |
| L2 (unified) | 256 KB – 1 MB | 10–15 cycles |
| L3 (shared) | 4–32 MB | 30–50 cycles |
| DRAM | GBs | 100–200 cycles |

AMAT = Hit time + Miss rate × Miss penalty (applies recursively).

## 6. Cache Replacement and Write Policies

- **LRU** (Least Recently Used): replace the block that was last used furthest in the past. Hardware cost grows with associativity.
- **Write-through**: every store also writes to the next cache level. Simple; generates bus traffic.
- **Write-back with dirty bit**: stores go only to the cache line; the line is written to memory only when evicted. Reduces traffic; requires coherence protocol.

## 7. Virtual Memory and TLB

Virtual memory gives each process the illusion of a private address space. The OS maintains page tables; the MMU translates virtual to physical addresses. The **TLB** (Translation Lookaside Buffer) caches recent translations.

TLB miss → page table walk → update TLB → retry access. A page fault occurs when the page is not in physical memory.

> **Interview answer:** "The TLB is a hardware cache of recent virtual-to-physical translations. On a miss the hardware page table walker (or software handler) fills the TLB. A page fault means the page is not present in physical RAM and the OS must fetch it from swap."

## 8. Out-of-Order Execution

Out-of-order processors issue instructions in dataflow order (when operands are ready) rather than program order. Key structures:

- **Reorder Buffer (ROB)**: holds in-flight instructions; commits in program order.
- **Reservation stations / issue queues**: hold instructions waiting for operands.
- **Register renaming (RAT)**: eliminates WAR and WAW hazards by mapping architectural registers to physical registers.

## 9. Branch Prediction

- **Static**: always predict not-taken (or backward branches taken for loops).
- **1-bit predictor**: one bit of history per branch; misses on loop exits.
- **2-bit saturating counter**: two bits of state; tolerates single mispredictions.
- **Tournament/hybrid predictor**: selects between local and global history predictors per branch.

Modern processors (e.g., TAGE predictor) use tagged, indexed global history and achieve >99% accuracy on typical workloads.

## 10. Performance Equation

$$\text{CPU Time} = \text{Instruction Count} \times \text{CPI} \times \text{Clock Period}$$

To improve performance: reduce IC (better algorithm or ISA), reduce CPI (better micro-architecture), reduce clock period (better circuit design / process node).

## Quick-Reference Cheat Sheet

| Concept | One-line answer |
|---|---|
| Forwarding | Routes ALU output directly to the input of a dependent instruction |
| Load-use hazard | One stall cycle required even with forwarding (memory result not ready) |
| Spectre/Meltdown | Exploit speculative execution and cache side channels to read privileged memory |
| Dennard scaling | As transistors shrink, power density stays constant — broke ~2005 |
| Moore's Law | Transistor count doubles ~every 2 years — slowing but not dead |
