# Set-Associative Cache Simulator

Simulate an N-way set-associative cache with LRU replacement and report the number of hits and misses for a sequence of memory accesses.

## Input

```
Line 1: C B N K
  C = number of sets (power of 2)
  B = bytes per cache line (power of 2)
  N = associativity (ways per set, N ≥ 1)
  K = number of memory accesses
Lines 2..K+1: one address per line (non-negative integer, byte address)
```

## Output

One line: `<hits> <misses>` (space-separated integers).

## Cache Behavior

- **Address decomposition**: `block_offset = addr mod B`, `set_index = (addr / B) mod C`, `tag = addr / (B * C)` (using integer division).
- **Replacement policy**: LRU (Least Recently Used) — when a set is full and a new block must be loaded, evict the block that was accessed least recently.
- Initially the cache is empty (all lines invalid).

## Example

```
Input:
2 4 2 6
0
16
0
16
0
16

Output: 4 2
```

Explanation: C=2, B=4, N=2 (2-way). Addresses 0 and 16 both map to set 0 (both have block_index 0 mod 2 = 0). The 2-way associativity lets both reside in set 0 simultaneously after the first two misses, so all subsequent accesses hit.
