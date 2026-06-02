# Video: Memory Hierarchy, Caches, and Locality

This video provides a visual deep-dive into the memory hierarchy and cache design. It demonstrates why locality of reference makes caches so effective, and walks through the address decomposition math for direct-mapped and set-associative caches.

**Key topics covered:**
- The memory hierarchy from registers to DRAM to NVMe SSD: latencies, bandwidths, capacities
- Temporal and spatial locality with concrete code examples
- Cache lines and block transfers; the three C's of cache misses (compulsory, capacity, conflict)
- Direct-mapped vs set-associative cache address decomposition (tag, index, offset)
- Write-through vs write-back policies and write buffers
- Average Memory Access Time (AMAT) formula and multi-level cache calculations

**Takeaway:** You will be able to decompose a memory address for any cache configuration, predict hit/miss patterns for access sequences, and use AMAT to compare cache design alternatives.
