# Prompt: Compute an ISR Address From a Vector Table

## Problem Statement

Simulate the x86 real-mode CPU's IVT (Interrupt Vector Table) lookup. Given a flat byte array representing a portion of the IVT and a list of vector numbers, decode the segment, offset, and linear address of the ISR for each requested vector.

### IVT Entry Format

Each entry is 4 bytes, little-endian:

```
byte[N*4 + 0] = offset_lo
byte[N*4 + 1] = offset_hi
byte[N*4 + 2] = segment_lo
byte[N*4 + 3] = segment_hi

offset  = offset_lo  + offset_hi  * 256
segment = segment_lo + segment_hi * 256
linear  = segment * 16 + offset
```

## Input Format

```
<num_bytes>
<byte0> <byte1> ... <byte_{num_bytes-1}>
<num_queries>
<vector0>
<vector1>
...
```

- `num_bytes`: integer, 4–1024, always a multiple of 4
- Bytes are space-separated decimal integers, each 0–255, all on one line
- `num_queries`: integer, 1–256
- Each `vectorN`: integer in range `[0, num_bytes/4 - 1]`

## Output Format

For each query (in order), print exactly one line:

```
Vector <N>: segment=<S> offset=<O> linear=<L>
```

All numeric values are decimal integers (no leading zeros, no padding).

## Constraints

- 4 ≤ num_bytes ≤ 1024
- num_bytes mod 4 == 0
- 1 ≤ num_queries ≤ 256
- 0 ≤ each vector ≤ (num_bytes / 4) - 1
- 0 ≤ each byte ≤ 255

## Sample Input

```
16
16 0 0 1 64 0 0 2 128 0 0 3 0 0 0 4
3
0
1
3
```

## Sample Output

```
Vector 0: segment=256 offset=16 linear=4112
Vector 1: segment=512 offset=64 linear=8256
Vector 3: segment=1024 offset=0 linear=16384
```

## Notes

- A vector may appear multiple times in the query list; output it each time.
- The linear address formula is exact: `segment * 16 + offset`. No modular arithmetic needed (max linear = 65535*16 + 65535 = 1,114,095, well within a 32-bit integer).
- No input validation required — all inputs are guaranteed valid.
