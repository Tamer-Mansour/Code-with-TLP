# Quiz: Multicore, Coherence, and Consistency

Test your understanding of multiprocessor architecture, cache coherence protocols, memory consistency models, and the RISC-V memory model.

---

**Q1. Why did processor clock frequencies stop scaling beyond ~4 GHz around 2004?**

- [ ] Transistors became too large to fit more on a chip
- [ ] Software could not run faster than 4 GHz
- [x] Leakage current and heat dissipation prevented further voltage/frequency scaling (the power wall)
- [ ] The memory wall caused caches to be too slow to feed a faster CPU

The collapse of Dennard scaling meant that shrinking transistors no longer kept power density constant — leakage current grew, and chips could not dissipate the resulting heat. Clock frequency stalled while transistor counts continued to grow, motivating the multicore shift.

---

**Q2. In the MESI protocol, a cache line in the Exclusive (E) state can be promoted to Modified (M) when the local processor writes to it. What bus transaction is required?**

- [ ] BusRd — a standard bus read
- [ ] BusRdX — a read-exclusive to invalidate other copies
- [x] No bus transaction — the promotion from E to M is silent
- [ ] BusWr — a broadcast write to update all caches

When a line is in the Exclusive state, the processor knows it is the sole copy and memory is up-to-date. Writing to it silently upgrades to Modified with zero bus traffic — one of MESI's key optimizations over the simpler MSI protocol.

---

**Q3. Thread 0 writes `x = 1`, then reads `y`. Thread 1 writes `y = 1`, then reads `x`. Both `x` and `y` start at 0. Under which memory model is the outcome `r0 = 0` and `r1 = 0` (both reads return 0) POSSIBLE?**

- [ ] Sequential Consistency (SC) only
- [ ] Total Store Order (TSO/x86) only
- [ ] Sequential Consistency and TSO
- [x] Total Store Order (TSO) and weaker models such as RVWMO

Under SC this outcome is impossible — at least one store must be globally visible before the other core's read. Under TSO the store enters a store buffer before becoming globally visible; both threads can read the old value from their own store buffers bypassing the other's not-yet-committed store, making `r0=0, r1=0` possible without a fence.

---

**Q4. Which RISC-V instruction sequence correctly implements a spinlock acquire using the LR/SC mechanism with acquire semantics?**

- [ ] `AMOADD.W t0, t1, (a0)` followed by `FENCE R, W`
- [x] `LR.W.AQ t0, (a0)` / check / `SC.W.RL t1, t2, (a0)` in a retry loop
- [ ] `FENCE RW, RW` followed by a plain `STORE` to the lock word
- [ ] `AMOSWAP.W t0, zero, (a0)` with no ordering annotation

Acquire semantics require that no memory operation following the load can be reordered before it. The `.AQ` annotation on `LR.W` provides this. The `.RL` on `SC.W` provides release semantics so that prior writes are visible before the lock is released. The retry loop handles the case where another hart writes the reservation address between LR and SC.

---

**Q5. A directory-based coherence protocol is preferred over a snooping protocol for large-scale systems primarily because:**

- [ ] It has lower latency for any cache miss
- [ ] It does not require maintaining state per cache line
- [x] Invalidation messages are sent only to the caches that actually hold a copy, avoiding O(N) broadcasts
- [ ] It eliminates the need for cache-to-cache transfers

In snooping, every coherence transaction is broadcast to all N processors, causing O(N) traffic per write. A directory explicitly tracks which caches hold each block, so invalidations are targeted only to those caches — O(k) where k is the number of actual sharers. This makes directory coherence scale to hundreds or thousands of cores.

---

**Q6. Two threads on separate cores each increment a different `long` counter, yet performance is far worse than single-threaded. The most likely cause is:**

- [ ] True sharing — both threads access the same counter
- [ ] A missing memory barrier causing incorrect results
- [x] False sharing — the two counters reside in the same 64-byte cache line, causing constant coherence invalidations
- [ ] NUMA effects — the counters are allocated on a remote memory node

False sharing occurs when logically independent variables share a physical cache line. Every write by Core 0 to `counter_a` invalidates Core 1's copy of the line (which also contains `counter_b`), forcing a re-fetch. The fix is to pad or `alignas(64)` each counter to its own cache line.
