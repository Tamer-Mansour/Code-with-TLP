# Exercise Prompt: Route Transactions Through an Address-Mapped Bus

## Problem Statement

You are implementing the address-decode core of a TLM bus model.

Given an address map and a list of transactions, decode each transaction's address to determine which target it hits, compute the target-local address (global address minus region base), and output the result.

Regions are **non-overlapping**. A transaction hits a region if:

```
region.base <= transaction.address < region.base + region.size
```

If no region matches, the transaction is `UNMAPPED`.

## Input Format

```
N M
name_0 base_0_hex size_0_hex
name_1 base_1_hex size_1_hex
...   (N lines)
addr_0_hex cmd_0 bytes_0
addr_1_hex cmd_1 bytes_1
...   (M lines)
```

- `N` — number of address map regions (1 ≤ N ≤ 20)
- `M` — number of transactions (1 ≤ M ≤ 50)
- `name_i` — target name, alphanumeric, no spaces
- `base_i_hex` — hex string (with or without `0x` prefix), 32-bit, base address of region
- `size_i_hex` — hex string, size of region in bytes (> 0)
- `addr_i_hex` — hex address of the transaction
- `cmd_i` — `R` (read) or `W` (write)
- `bytes_i` — integer, data length in bytes (not used for decode, included for realism)

## Output Format

For each transaction, output one line:

```
TARGET local_addr_hex
```

- `TARGET` — the region name if matched, or `UNMAPPED` if no region covers the address
- `local_addr_hex` — 8-digit zero-padded lowercase hex (e.g., `0x00000008`), or `----------` for UNMAPPED

## Sample Input

```
4 6
ROM      0x00000000 0x00010000
SRAM     0x20000000 0x00020000
UART     0x40000000 0x00001000
GPIO     0x40001000 0x00001000
0x00000000 R 4
0x20000100 W 8
0x40000008 R 4
0x40001004 W 4
0x50000000 R 4
0x0000FFFF R 1
```

## Sample Output

```
ROM 0x00000000
SRAM 0x00000100
UART 0x00000008
GPIO 0x00000004
UNMAPPED ----------
ROM 0x0000ffff
```

## Constraints

- All addresses and sizes fit in a 32-bit unsigned integer.
- Regions are guaranteed non-overlapping.
- Transaction address is always within 32-bit range.
- Output local address in lowercase hex, 8 digits, prefixed with `0x`.
- Output `----------` (10 dashes) as the local address for UNMAPPED transactions.

## Notes

- Parse hex strings with Python's `int(s, 16)` or `int(s, 0)` (handles the optional `0x` prefix).
- The output target name must match the input name exactly (case-sensitive).
- Process transactions in the order they appear in input.
