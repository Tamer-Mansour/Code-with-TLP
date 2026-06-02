# Prompt: Detect Overlapping Regions in an Address Map

## Problem Statement

A TLM router must reject address maps that contain overlapping regions. Given a list of named memory regions, find and report all pairs of regions whose address ranges overlap.

Two regions A and B overlap if there exists at least one address that belongs to both:

```
overlap iff  A.base < B.base + B.size  AND  B.base < A.base + A.size
```

## Input Format

```
Line 1:    N   (integer, 1 <= N <= 20)
Lines 2..N+1:  <name> <base_hex> <size_hex>
               base_hex and size_hex use "0x" prefix (lowercase hex)
```

## Output Format

- For each overlapping pair, print one line: `<name1> <name2>`
  where `name1 < name2` lexicographically (alphabetical order).
- Print all pairs sorted lexicographically by `(name1, name2)`.
- If there are no overlapping pairs, print `OK`.

## Constraints

- All addresses and sizes fit in a 64-bit unsigned integer.
- Region sizes are at least 1 byte.
- Region names are unique, contain only alphanumeric characters and underscores.
- 1 <= N <= 20.

## Sample Input 1 — No Overlaps

```
3
Flash 0x08000000 0x00080000
SRAM 0x20000000 0x00020000
GPIOA 0x40023800 0x00000400
```

## Sample Output 1

```
OK
```

## Sample Input 2 — One Overlap

```
3
RegA 0x10000000 0x00010000
RegB 0x10008000 0x00010000
RegC 0x30000000 0x00001000
```

## Sample Output 2

```
RegA RegB
```

Explanation: RegA covers `[0x10000000, 0x10010000)` and RegB covers `[0x10008000, 0x10018000)`. They overlap in `[0x10008000, 0x10010000)`. RegC does not overlap either.

## Sample Input 3 — Multiple Overlaps

```
4
Alpha 0x00001000 0x00002000
Beta  0x00002000 0x00002000
Gamma 0x00000000 0x00005000
Delta 0x00010000 0x00001000
```

## Sample Output 3

```
Alpha Beta
Alpha Gamma
Beta Gamma
```

Explanation:
- Alpha `[0x1000, 0x3000)` and Beta `[0x2000, 0x4000)` overlap at `[0x2000, 0x3000)`.
- Gamma `[0x0000, 0x5000)` contains both Alpha and Beta entirely.
- Delta `[0x10000, 0x11000)` does not overlap any other region.
- Pairs are sorted: `(Alpha,Beta)`, `(Alpha,Gamma)`, `(Beta,Gamma)`.
