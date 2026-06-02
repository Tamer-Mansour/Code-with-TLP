# Exercise: Map Addresses to Devices via Decoding

## Problem Statement

You are simulating a hardware address decoder. The system has `N` memory-mapped devices, each assigned a contiguous range of the address space defined by a **base address** and a **size** in bytes. Your decoder receives `D` query addresses and must identify which device each address belongs to, or output `UNMAPPED` if the address falls in no device's range.

A device occupies addresses `[base, base + size - 1]` inclusive.

You may assume ranges do not overlap (the system is correctly configured).

## Input Format

```
N D
name1 base1_hex size1_hex
name2 base2_hex size2_hex
...
addr1_hex
addr2_hex
...
```

- Line 1: two integers `N` (number of devices, 1 ≤ N ≤ 100) and `D` (number of queries, 1 ≤ D ≤ 100).
- Next `N` lines: a device name (alphanumeric, no spaces, ≤ 16 chars), a base address in hexadecimal (no `0x` prefix), and a size in hexadecimal (no `0x` prefix).
- Next `D` lines: one query address per line in hexadecimal (no `0x` prefix).

All addresses and sizes fit in an unsigned 32-bit integer (0 to FFFFFFFF).

## Output Format

Print exactly `D` lines. For each query address, print the name of the device whose range contains it, or `UNMAPPED` if no device covers it.

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ D ≤ 100
- All hex values are valid unsigned 32-bit integers (up to 8 hex digits).
- Device ranges do not overlap.
- Device names contain only letters, digits, and underscores.

## Sample Input

```
4 5
RAM 00000000 10000000
ROM 10000000 00001000
UART 20000000 00001000
GPIO 20001000 00001000
00000000
0FFFFFFF
10000000
20001500
30000000
```

## Sample Output

```
RAM
RAM
ROM
GPIO
UNMAPPED
```

## Explanation

- Device ranges: RAM covers `0x00000000–0x0FFFFFFF`; ROM covers `0x10000000–0x10000FFF`; UART covers `0x20000000–0x20000FFF`; GPIO covers `0x20001000–0x20001FFF`.
- `0x00000000` → RAM (start of RAM range).
- `0x0FFFFFFF` → RAM (last byte of RAM range).
- `0x10000000` → ROM (first byte of ROM range).
- `0x20001500` → GPIO (within `0x20001000–0x20001FFF`).
- `0x30000000` → UNMAPPED (no device covers this address).
