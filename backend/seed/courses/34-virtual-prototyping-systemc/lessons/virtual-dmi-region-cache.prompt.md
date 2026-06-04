# Exercise: Direct Memory Interface (DMI) Region Cache Lookup

## Problem Statement

In TLM-2.0, the Direct Memory Interface (DMI) allows an initiator to obtain a pointer to a target's memory region, bypassing the transaction socket for subsequent accesses. The initiator maintains a DMI cache of granted regions. Each entry has: `start_address`, `end_address`, `access_type` (`R`=read-only, `W`=write-only, `RW`=read-write).

When an access arrives, the initiator checks the DMI cache:
- If a cache entry covers the address AND supports the requested access type, it is a `DMI_HIT`.
- Otherwise it is a `DMI_MISS` and a full TLM transaction must be issued.

For a READ request: the entry must have access_type `R` or `RW`.
For a WRITE request: the entry must have access_type `W` or `RW`.

Given a DMI cache state and a list of memory access requests, for each request print `HIT: DMI region [<start>-<end>] <access_type>` or `MISS`.

Check entries in order; report the first matching entry.

## Input Format

- Line 1: `E` (number of DMI cache entries, 1 <= E <= 10)
- Next E lines: `<start_address> <end_address> <access_type>`
- Line E+2: `N` (number of access requests, 1 <= N <= 20)
- Next N lines: `<address> <READ|WRITE>`

## Output Format

- N lines, one per access request

## Constraints

- 1 <= E <= 10
- 1 <= N <= 20
- All addresses are non-negative integers
- Addresses fit in a 32-bit unsigned integer

## Sample Input

```
3
0 1023 R
1024 2047 RW
2048 4095 W
5
512 READ
512 WRITE
1500 READ
1500 WRITE
3000 READ
```

## Sample Output

```
HIT: DMI region [0-1023] R
MISS
HIT: DMI region [1024-2047] RW
HIT: DMI region [1024-2047] RW
MISS
```

## Additional Example

Input:
```
2
0 255 RW
256 511 R
4
0 READ
0 WRITE
300 READ
300 WRITE
```

Output:
```
HIT: DMI region [0-255] RW
HIT: DMI region [0-255] RW
HIT: DMI region [256-511] R
MISS
```
