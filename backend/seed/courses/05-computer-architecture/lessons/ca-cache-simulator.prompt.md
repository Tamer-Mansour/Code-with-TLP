# Cache Hit/Miss Simulator

Simulate a **direct-mapped cache** and count hits and misses for a sequence of memory accesses.

## Input Format

```
C B N
addr_0
addr_1
...
addr_{N-1}
```

- `C` — number of cache sets (a power of 2, 1 ≤ C ≤ 256)
- `B` — cache line size in bytes (a power of 2, 1 ≤ B ≤ 64)
- `N` — number of memory accesses (1 ≤ N ≤ 1000)
- Each `addr_i` is a non-negative integer (byte address, fits in a 32-bit unsigned integer)

The cache starts empty (cold). Each access is a **read**.

## Output Format

Two integers on one line separated by a space:
```
hits misses
```

## Example

**Input:**
```
4 4 6
0
4
8
0
16
4
```

**Explanation:**
- C=4 sets, B=4 bytes/line → offset bits=2, index bits=2
- Address 0:  index=0, tag=0 → MISS (load line)
- Address 4:  index=1, tag=0 → MISS
- Address 8:  index=2, tag=0 → MISS
- Address 0:  index=0, tag=0 → HIT
- Address 16: index=0, tag=1 → MISS (conflict evicts tag=0 from set 0)
- Address 4:  index=1, tag=0 → HIT

**Output:**
```
2 4
```
