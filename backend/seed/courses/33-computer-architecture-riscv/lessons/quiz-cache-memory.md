# Quiz: Cache Memory

**Q1. A 32-bit address is used with a cache that has a 64-byte line size and 128 sets (direct-mapped). How many bits are used for the tag field?**

- [ ] 17 bits
- [x] 19 bits
- [ ] 21 bits
- [ ] 13 bits

offset_bits = log2(64) = 6; index_bits = log2(128) = 7; tag_bits = 32 - 6 - 7 = 19.

---

**Q2. Which type of cache miss occurs even in a fully associative cache with unlimited capacity?**

- [ ] Conflict miss
- [ ] Capacity miss
- [x] Compulsory (cold) miss
- [ ] Coherence miss

Compulsory misses happen on the very first access to any block. No cache organisation or size can eliminate them because the data has simply never been loaded before.

---

**Q3. A write-back cache with write-allocate suffers a write miss. What does the hardware do next?**

- [ ] Write the data directly to RAM and discard it from cache
- [ ] Stall until the line is written to RAM, then proceed
- [x] Fetch the target block from RAM into cache, write the new data in cache, and set the dirty bit
- [ ] Broadcast the write to all cache levels simultaneously

Write-back + write-allocate: on a write miss, the block is first fetched (allocated) into cache, the write is performed in cache, and the dirty bit is set. The updated line reaches RAM only when eventually evicted.

---

**Q4. Two threads on separate cores both frequently update different fields of the same 64-byte struct. Performance is far worse than expected. What is the most likely cause?**

- [ ] The threads are using write-through caches
- [ ] The struct is too large to fit in any cache line
- [x] False sharing — both fields sit in the same cache line, triggering coherence traffic between cores
- [ ] FIFO replacement is evicting the struct before each access

False sharing occurs when independent data that happens to share a cache line causes the coherence protocol to invalidate and re-fetch that line on every cross-core write, even though neither thread reads the other's data.

---

**Q5. Which replacement policy can exhibit Belady's anomaly — adding more cache ways sometimes increases the miss rate?**

- [ ] LRU
- [ ] Optimal (OPT)
- [x] FIFO
- [ ] Pseudo-LRU

Belady's anomaly affects FIFO and some other stack-non-property policies. LRU and OPT are "stack algorithms" — adding capacity never makes them worse.

---

**Q6. A program's inner loop processes a 256 KB array. The L2 cache is 128 KB. After carefully measuring, you find the miss rate is identical whether the cache is direct-mapped or 16-way set-associative. What type of miss dominates?**

- [ ] Conflict misses
- [x] Capacity misses
- [ ] Compulsory misses
- [ ] Coherence misses

If changing associativity (which fixes conflict misses) has no effect, the working set simply does not fit in the cache — a capacity problem. The fix is a larger cache or loop tiling, not higher associativity.
