# Exercise: Compute an ISR Address From a Vector Table

In this exercise you will simulate the lookup the CPU performs when an interrupt fires in x86 real mode — reading a handler's address out of the **Interrupt Vector Table** (IVT).

## Background

In x86 real mode the IVT lives at physical address `0x00000` and contains up to 256 entries. Each entry is **4 bytes** in little-endian order:

```
byte[N*4 + 0]  =  offset_lo   (bits 7:0 of handler offset)
byte[N*4 + 1]  =  offset_hi   (bits 15:8 of handler offset)
byte[N*4 + 2]  =  segment_lo  (bits 7:0 of handler segment)
byte[N*4 + 3]  =  segment_hi  (bits 15:8 of handler segment)
```

To reconstruct the values:

```python
offset  = offset_lo  + offset_hi  * 256
segment = segment_lo + segment_hi * 256
linear  = segment * 16 + offset    # real-mode linear address
```

## What You Will Implement

Read a sequence of IVT bytes and a list of interrupt vector numbers. For each vector, decode the ISR segment, offset, and linear address.

## Input Format

```
<num_bytes>
<byte0> <byte1> ... <byte_{num_bytes-1}>
<num_queries>
<vector0>
<vector1>
...
```

- `num_bytes` is a multiple of 4 (4–1024)
- Each byte is a decimal integer 0–255
- Each vector index is in range `[0, num_bytes/4 - 1]`

## Output Format

One line per query:

```
Vector <N>: segment=<S> offset=<O> linear=<L>
```

All values are decimal integers.

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

## Walkthrough

For vector 0, bytes at positions [0..3] = `[16, 0, 0, 1]`:
- `offset  = 16 + 0×256 = 16`
- `segment = 0 + 1×256 = 256`
- `linear  = 256×16 + 16 = 4096 + 16 = 4112`

For vector 3, bytes at positions [12..15] = `[0, 0, 0, 4]`:
- `offset  = 0`
- `segment = 0 + 4×256 = 1024`
- `linear  = 1024×16 + 0 = 16384`
