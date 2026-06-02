# Parse a Hexdump and Reconstruct Values

Parsing a hexdump by hand is a skill every embedded engineer needs. In this exercise you will write a program that reads a simplified hexdump from stdin, reconstructs multi-byte integer values from it using a specified byte order, and reports the results.

## What You Will Implement

Your program receives:

1. An endianness specifier (`LE` or `BE`).
2. A series of hexdump lines in canonical `hexdump -C` style (address, then space-separated byte pairs).
3. A list of queries: each query provides an address and a width (1, 2, or 4 bytes), and you must return the integer value stored at that address using the given endianness.

## Key Steps

**Step 1 — Parse the hexdump into a byte dictionary.** Map each address (offset) to its byte value.

```python
memory = {}
for line in hexdump_lines:
    parts = line.split()
    base_addr = int(parts[0], 16)
    for i, byte_str in enumerate(parts[1:]):
        memory[base_addr + i] = int(byte_str, 16)
```

**Step 2 — Reconstruct a value from N consecutive bytes.** For little-endian, byte at the lowest address is the LSB:

```python
def read_le(memory, addr, width):
    result = 0
    for i in range(width):
        result |= memory[addr + i] << (8 * i)
    return result
```

For big-endian, byte at the lowest address is the MSB:

```python
def read_be(memory, addr, width):
    result = 0
    for i in range(width):
        result = (result << 8) | memory[addr + i]
    return result
```

**Step 3 — Format the output.** Print the value as an uppercase hex string zero-padded to `2 * width` digits.

## Example

Given the hexdump line:

```
00000000  78 56 34 12  de ad be ef
```

With endianness `LE`, a query for address `0x0000`, width `4` reconstructs:
bytes `78 56 34 12` → LE word `0x12345678`.

With endianness `BE`, the same query gives `0x78563412`.

## Your Task

Read the full problem specification, input format, and test cases from the accompanying prompt file, then implement the solution in Python using only the standard library.
