# Video: Arrays & Dynamic Arrays — Full Walkthrough

This video covers how arrays are laid out in memory, why random access is O(1), and how dynamic arrays (Python lists, C++ `std::vector`) grow using an amortised doubling strategy.

**Key takeaways:**
- Contiguous memory layout and cache-line locality explain why sequential array access is so fast in practice.
- The amortised O(1) cost of `append` comes from the doubling strategy — resizes are rare and their cost is spread over many insertions.
- Knowing when to prefer arrays over linked structures (O(1) index access vs. O(n) traversal) is a foundational interview skill.

**Approximate timestamps:**
- 0:00 — Static arrays and memory addressing
- 8:00 — Dynamic arrays, growth factor, and amortised analysis
- 18:00 — Python list internals and the `array` module
- 26:00 — Common array patterns: two-pointer, sliding window, prefix sums
