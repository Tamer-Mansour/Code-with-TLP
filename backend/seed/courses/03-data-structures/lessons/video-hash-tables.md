# Video: Hash Tables — Hashing, Collisions, and Python Dicts

This video covers how hash functions map keys to buckets, how chaining and open addressing handle collisions, and what load factor and rehashing mean for real-world performance.

**Key takeaways:**
- A good hash function distributes keys uniformly — poor distribution causes O(n) worst-case lookup even with a hash table.
- Python's `dict` uses open addressing with pseudo-random probing; understanding this helps you avoid hidden performance cliffs (e.g., many deletions increasing probe lengths).
- The two-sum pattern (store complements in a dict as you iterate) is the canonical O(n) hash-table algorithm that appears in hundreds of interview problems.

**Approximate timestamps:**
- 0:00 — Hash function design and the division/multiplication methods
- 10:00 — Collision resolution: chaining vs. open addressing (linear probe, quadratic probe)
- 22:00 — Load factor, rehashing, and amortised O(1) guarantees
- 32:00 — Python `dict` and `set` internals
- 40:00 — Interview patterns: frequency counting, two-sum, grouping anagrams
