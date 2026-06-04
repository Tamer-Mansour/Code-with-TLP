# Direct-Mapped Cache Simulator

## Problem Description

Simulate a **direct-mapped cache** with a write-allocate policy.

Input begins with a header line in the format:

```
CACHE <cache_size_bytes> <block_size_bytes>
```

Both values are powers of 2. Following lines are memory accesses in the format:

```
<R|W> <hex_address>
```

where `R` means read and `W` means write. The hex address has no `0x` prefix.

For each memory access, print `HIT` if the block is in the cache, or `MISS` if it is not.

**On a MISS**, the block is always loaded into the cache (replacing the existing block in that slot, which is evicted silently). This applies to both reads and writes (**write-allocate**: on a write miss, load the block first, then write).

After all accesses, print a single summary line:

```
hits=<N> misses=<N> hit_rate=<X.XX%>
```

where the hit rate is `hits / total_accesses * 100`, formatted to exactly 2 decimal places followed by `%`.

## Cache Mechanics

For a direct-mapped cache with `cache_size` bytes and `block_size` bytes per block:

```
num_sets    = cache_size / block_size
offset_bits = log2(block_size)
index_bits  = log2(num_sets)
index       = (address >> offset_bits) & (num_sets - 1)
tag         = address >> (offset_bits + index_bits)
```

A HIT occurs when `cache[index].valid == True` and `cache[index].tag == tag`.  
A MISS replaces: `cache[index] = (tag, valid=True)`.

## Input Format

```
CACHE <cache_size_bytes> <block_size_bytes>
<R|W> <hex_address>
<R|W> <hex_address>
...
```

- `cache_size_bytes` and `block_size_bytes` are powers of 2.
- `cache_size_bytes` is between 16 and 65536 inclusive.
- `block_size_bytes` is between 4 and 256 inclusive and divides `cache_size_bytes`.
- Hex addresses are 1–8 uppercase or lowercase hex digits (no `0x` prefix).
- 1 ≤ number of accesses ≤ 1000.

## Output Format

One line per access (`HIT` or `MISS`), then one summary line.

## Sample Input

```
CACHE 64 16
R 00000000
R 00000004
R 00000010
R 00000000
W 00000040
R 00000000
R 00000010
```

## Sample Output

```
MISS
HIT
MISS
HIT
MISS
MISS
HIT
hits=3 misses=4 hit_rate=42.86%
```

## Explanation

Cache configuration: 64 bytes total, 16 bytes per block → 4 sets (index bits = 2, offset bits = 4).

| Access        | Address | index | tag | Cache state after        | Result |
|---------------|---------|-------|-----|--------------------------|--------|
| R 0x00000000  | 0       | 0     | 0   | set0=tag0                | MISS   |
| R 0x00000004  | 4       | 0     | 0   | set0=tag0 (same block)   | HIT    |
| R 0x00000010  | 16      | 1     | 0   | set1=tag0                | MISS   |
| R 0x00000000  | 0       | 0     | 0   | set0=tag0 (still there)  | HIT    |
| W 0x00000040  | 64      | 0     | 1   | set0=tag1 (evicts tag0)  | MISS   |
| R 0x00000000  | 0       | 0     | 0   | set0=tag0 (reloaded)     | MISS   |
| R 0x00000010  | 16      | 1     | 0   | set1=tag0 (unchanged)    | HIT    |

Total: 7 accesses, 3 hits, 4 misses. hit_rate = 3/7 × 100 = 42.857...% → 42.86%.

## Additional Sample Input

```
CACHE 256 32
R 00000000
R 00000020
R 00000100
R 00000000
W 00000020
R 00000100
```

## Additional Sample Output

```
MISS
MISS
MISS
HIT
HIT
HIT
hits=3 misses=3 hit_rate=50.00%
```

## Constraints

- `cache_size_bytes` is a power of 2 in [16, 65536].
- `block_size_bytes` is a power of 2 in [4, 256] and ≤ `cache_size_bytes`.
- All addresses are non-negative 32-bit values.
- 1 ≤ number of accesses ≤ 1000.
- Use only the Python standard library.
- Time limit: 3000 ms
- Memory limit: 256 MB
