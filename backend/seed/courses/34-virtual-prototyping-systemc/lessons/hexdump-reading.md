# Reading a Hexdump of Memory

A hexdump is a textual representation of raw memory contents. Every embedded engineer reads hexdumps when debugging firmware, inspecting register state, analysing crash dumps, or verifying DMA transfers. Being fluent with hexdump notation is a basic professional skill.

## The Standard Hexdump Layout

The classic `hexdump -C` (or `xxd`) format shows:

```
00000000  de ad be ef  00 00 00 01  12 34 56 78  ab cd ef 00  |........ .4Vx....|
00000010  ff ff ff ff  00 00 00 00                             |........        |
```

| Column | Meaning |
|---|---|
| `00000000` | Address (offset from start of region), 8 hex digits |
| Hex groups | 16 bytes of raw data, two hex digits per byte, space-separated |
| `|...|` | ASCII printable representation; `.` for non-printable bytes |

Each line covers 16 bytes. If the last line is shorter, it is padded with spaces in the hex section.

## Reading Values From a Hexdump

**Step 1 — Find the base address.** The leftmost column is the offset.

**Step 2 — Count bytes.** Each two-digit group is one byte. Groups are ordered left-to-right at ascending addresses.

**Step 3 — Account for endianness.** If the target is little-endian and you want the 32-bit value at offset `0x0000`, read four bytes left to right (`DE AD BE EF`) then reverse to reconstruct the integer: `0xEFBEADDE`. If the target is big-endian, read them left to right directly: `0xDEADBEEF`.

## Worked Example

```
00000000  78 56 34 12  00 10 20 30  ff 00 ff 00  a1 b2 c3 d4
```

Assuming **little-endian** memory:

| Offset | Raw bytes | 32-bit LE value |
|---|---|---|
| 0x00 | `78 56 34 12` | `0x12345678` |
| 0x04 | `00 10 20 30` | `0x30201000` |
| 0x08 | `ff 00 ff 00` | `0x00FF00FF` |
| 0x0C | `a1 b2 c3 d4` | `0xD4C3B2A1` |

If the same dump came from a **big-endian** system:

| Offset | Raw bytes | 32-bit BE value |
|---|---|---|
| 0x00 | `78 56 34 12` | `0x78563412` |

The bytes are identical — only the interpretation changes.

## Generating Hexdumps

```bash
# Linux / macOS — show canonical hexdump
hexdump -C binary_file.bin

# xxd — slightly different format, widely available
xxd binary_file.bin

# Python — dump a bytearray
import binascii
data = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01, 0x02, 0x03])
print(binascii.hexlify(data, ' ').upper())
# DE AD BE EF 00 01 02 03
```

## Identifying Data Types in a Dump

- Four identical bytes (e.g., `00 00 00 00`) often indicate a zeroed field or a null pointer.
- A repeating pattern (`FF FF FF FF`) may be flash memory that was never programmed.
- ASCII strings appear as printable characters in the rightmost column, making them easy to spot.
- Magic numbers at offset 0 identify file formats: ELF starts with `7F 45 4C 46` (`\x7FELF`), PNG with `89 50 4E 47`.

## Common Pitfalls

- **Forgetting endianness** — the most common mistake when reconstructing multi-byte values.
- **Off-by-one in address arithmetic** — the address column counts bytes, not words.
- **Mistaking the ASCII column** — `.` means "non-printable", not a literal dot.
- **Line wrap at 16 bytes** — a field that spans a 16-byte boundary appears split across two lines.

## Interview Answer

> "A hexdump shows raw memory as two-digit hex bytes, one byte per group, in ascending address order. To reconstruct a multi-byte integer, collect the bytes at the correct offset and reverse their order if the target is little-endian. The address column and the ASCII column are visual aids — only the hex byte groups carry data."
