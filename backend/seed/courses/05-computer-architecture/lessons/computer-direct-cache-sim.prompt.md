# Direct-Mapped Cache Simulator

Simulate a direct-mapped cache. Given the cache parameters and a sequence of memory addresses, determine HIT or MISS for each access and report the final hit rate.

## Cache Organization

A direct-mapped cache maps each memory address to exactly one cache line. The address is split into three fields:

```
| tag bits | index bits | offset bits |
```

- **offset bits** = log2(BLOCK_SIZE): select byte within the block
- **index bits** = log2(CACHE_SIZE / BLOCK_SIZE): select the cache line
- **tag bits**: remaining upper bits; identify which memory block occupies this cache line

On each access:
- Compute `index` and `tag` from the address.
- If `cache[index].valid` and `cache[index].tag == tag`: **HIT**
- Otherwise: **MISS** — load the block and update `cache[index].tag`

## Input Format

```
Line 1: CACHE_SIZE BLOCK_SIZE ADDRESS_BITS   (space-separated integers; CACHE_SIZE and BLOCK_SIZE are powers of 2)
Line 2: M   (number of memory accesses)
Lines 3..M+2: one hex address per line (e.g. 0x1A4)
```

## Output Format

For each of the M accesses, print `HIT` or `MISS` on its own line.  
After all accesses, print the hit rate: `Hit rate: X.XX%` (2 decimal places).

## Examples

**Example 1**
```
Input:
16 4 8
6
0x00
0x04
0x08
0x00
0x04
0x10

Output:
MISS
MISS
MISS
HIT
HIT
MISS
Hit rate: 33.33%
```

Explanation: CACHE_SIZE=16, BLOCK_SIZE=4 → 4 cache lines; offset_bits=2, index_bits=2.
- 0x00 (index=0, tag=0): MISS
- 0x04 (index=1, tag=0): MISS
- 0x08 (index=2, tag=0): MISS
- 0x00 (index=0, tag=0): HIT (still in cache)
- 0x04 (index=1, tag=0): HIT
- 0x10=16 (index=0, tag=1): MISS (conflicts with 0x00 — same index, different tag)

**Example 2 — Conflict miss**
```
Input:
16 4 8
5
0x00
0x10
0x00
0x10
0x00

Output:
MISS
MISS
MISS
MISS
MISS
Hit rate: 0.00%
```

Explanation: 0x00 and 0x10 both map to index 0, thrashing every access.

## Hints

- Use integer arithmetic (not floating-point) for bit extraction.
- `offset_bits = log2(BLOCK_SIZE)`, `index_bits = log2(num_lines)` where `num_lines = CACHE_SIZE // BLOCK_SIZE`
- `index = (addr >> offset_bits) & (num_lines - 1)`
- `tag = addr >> (offset_bits + index_bits)`
