# Quiz: Memory Fundamentals and Hierarchy

**Q1. Which memory technology uses 6 transistors per bit and requires no refresh?**
- [ ] DRAM
- [x] SRAM
- [ ] NAND flash
- [ ] NOR flash

SRAM uses a 6-transistor bistable latch that holds its state as long as power is applied, with no capacitor drain and therefore no refresh needed. DRAM uses 1 transistor + 1 capacitor and must be refreshed every ~64 ms.

---

**Q2. A cache has a hit time of 3 cycles, a miss rate of 10%, and the miss penalty is 90 cycles. What is the AMAT?**
- [ ] 93 cycles
- [ ] 9 cycles
- [x] 12 cycles
- [ ] 3 cycles

AMAT = Hit Time + Miss Rate × Miss Penalty = 3 + 0.10 × 90 = 3 + 9 = 12 cycles.

---

**Q3. Which of the following best describes spatial locality?**
- [ ] A value used recently will be used again soon
- [ ] Programs access a small working set that fits in L1 cache
- [x] If a memory address is accessed, nearby addresses are likely to be accessed soon
- [ ] Sequential instructions execute without branches

Spatial locality means that access to address X makes access to X±1, X±2, … likely in the near future. Caches exploit this by fetching an entire 64-byte cache line on each miss, not just the requested byte.

---

**Q4. Why does DRAM latency improve so slowly compared to CPU speed?**
- [ ] DRAM manufacturers lack incentive to improve it
- [ ] DRAM latency is already fast enough for modern workloads
- [x] Row activation physics (RC delay on bit lines) is a fundamental bottleneck that does not shrink proportionally with transistor scaling
- [ ] DRAM latency is limited by software drivers, not hardware

The time to charge a DRAM row's bit lines is governed by the RC time constant of the metal wire. As cells shrink, resistance increases and capacitance decreases in a way that keeps the RC product roughly constant, preventing significant latency improvements.

---

**Q5. A program traverses a singly-linked list with nodes scattered throughout the heap. Which performance problem does this most directly illustrate?**
- [ ] High arithmetic intensity
- [ ] Cache line aliasing
- [x] Poor spatial locality leading to frequent cache misses
- [ ] Write amplification in NAND flash

Pointer-chasing through a linked list causes each node's address to be effectively random — each access likely misses the cache and loads an entirely new cache line, most of which will never be used.

---

**Q6. Which statement about the memory wall is most accurate?**
- [ ] CPU speed and DRAM latency have improved at roughly the same rate since 1980
- [ ] The memory wall was solved by the introduction of DDR4 memory
- [ ] The memory wall affects only GPU workloads
- [x] CPU performance has improved far faster than DRAM latency, causing CPUs to stall for hundreds of cycles on cache misses

The memory wall describes the widening gap: CPU speed improved ~60%/year while DRAM latency improved only ~7%/year. A modern CPU stalls for 200–300 cycles on a last-level cache miss, which is why large caches, prefetchers, and out-of-order execution are critical mitigations.
