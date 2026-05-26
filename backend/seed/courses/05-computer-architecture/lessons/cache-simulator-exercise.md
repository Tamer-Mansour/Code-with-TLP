# Exercise: Cache Hit/Miss Simulator

Apply your understanding of direct-mapped cache address decomposition by simulating a cache and counting hits and misses.

## Background

In a direct-mapped cache with C sets and B bytes per line:

- **Offset** = log2(B) least significant bits — byte position within the line.
- **Index** = next log2(C) bits — which cache set to look in.
- **Tag** = remaining bits — compared against the stored tag to confirm a hit.

On a miss, the new line is loaded (the old line in that set is evicted).

## Your Task

Given C, B, and a sequence of N byte addresses, simulate the cache and output the total number of hits and misses.

See the exercise panel for the full specification and examples.
