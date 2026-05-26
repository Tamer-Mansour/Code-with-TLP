# Quiz: Memory Hierarchy and Caches

**Q1. A 32 KB direct-mapped cache with 64-byte cache lines has how many sets?**
- [ ] 32
- [ ] 128
- [x] 512
- [ ] 1024

**Q2. Spatial locality explains why cache lines are 64 bytes rather than 1 byte because:**
- [ ] 64-byte lines reduce the number of tag bits needed.
- [x] When one byte is accessed, nearby bytes are likely to be needed soon; loading them together in a 64-byte line converts future misses into hits.
- [ ] 64 bytes is the width of a DDR4 memory bus.
- [ ] Larger lines make the cache associativity cheaper.

**Q3. For an address with a 6-bit block offset, a 7-bit set index, and 19-bit tag (32-bit address space), the cache has how many sets?**
- [ ] 64
- [x] 128
- [ ] 256
- [ ] 512

**Q4. Two addresses A and B map to the same cache set in a direct-mapped cache. Repeatedly accessing A then B in a tight loop causes:**
- [ ] A capacity miss on each access
- [ ] A compulsory miss on every access
- [x] A conflict miss on every access (each evicts the other from the single slot)
- [ ] No extra misses; both fit in the cache simultaneously

**Q5. With write-back caching, main memory is updated:**
- [ ] On every write, synchronously with the CPU store instruction.
- [x] When a modified (dirty) cache line is evicted from the cache.
- [ ] Every N cycles by a background refresh circuit.
- [ ] Only when the OS flushes the cache explicitly.

**Q6. Using the AMAT formula with L1 hit time=1, L1 miss rate=10%, and memory miss penalty=50 cycles, the AMAT is:**
- [ ] 5.1 cycles
- [x] 6 cycles
- [ ] 51 cycles
- [ ] 1.1 cycles
