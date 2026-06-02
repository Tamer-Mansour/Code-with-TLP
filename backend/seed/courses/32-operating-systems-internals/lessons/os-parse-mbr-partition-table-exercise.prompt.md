# Prompt: Parse an MBR Partition Table From Raw Bytes

## Problem Statement

You are given 512 bytes representing a raw Master Boot Record (MBR), encoded as exactly 512 space-separated hexadecimal byte values on a single line of stdin (e.g., `00 00 ... 55 AA`).

Parse the MBR partition table and print one line per **non-empty** partition entry.

## Input Format

- A single line containing exactly 512 space-separated hex byte values (two hex digits each, lowercase or uppercase).
- The bytes represent the full 512-byte MBR sector.

## Output Format

For each non-empty partition entry (entries where either `lba_start` or `lba_size` is non-zero), print exactly one line:

```
Partition <N>: Bootable=<Yes|No> Type=0x<TT> LBAStart=<start> LBASize=<size>
```

Where:
- `<N>` is the 1-based partition number (1–4)
- `<Yes|No>` is `Yes` if the status byte is `0x80`, otherwise `No`
- `<TT>` is the partition type byte as exactly 2 uppercase hex digits (e.g., `83`, `82`, `0B`)
- `<start>` is the LBA start as a decimal integer
- `<size>` is the LBA size as a decimal integer

If the MBR boot signature (bytes at offsets 510 and 511) is not `0x55 0xAA`, print exactly:
```
Invalid MBR signature
```
and produce no other output.

Empty entries (both `lba_start == 0` and `lba_size == 0`) must be skipped silently.

## Field Offsets (reference)

```
MBR structure:
  Offset 0–445:   Boot code (ignore)
  Offset 446–461: Partition entry 1 (16 bytes)
  Offset 462–477: Partition entry 2 (16 bytes)
  Offset 478–493: Partition entry 3 (16 bytes)
  Offset 494–509: Partition entry 4 (16 bytes)
  Offset 510:     Boot signature byte 1 (must be 0x55)
  Offset 511:     Boot signature byte 2 (must be 0xAA)

Each 16-byte partition entry:
  Byte 0:      Status (0x80 = bootable, 0x00 = not)
  Bytes 1–3:   CHS of first sector (ignore)
  Byte 4:      Partition type
  Bytes 5–7:   CHS of last sector (ignore)
  Bytes 8–11:  LBA start (little-endian uint32)
  Bytes 12–15: LBA size  (little-endian uint32)
```

## Constraints

- Input is always exactly 512 space-separated hex values.
- LBA values fit in a 32-bit unsigned integer (0 to 4,294,967,295).
- Partition type is a single byte (0x00–0xFF).
- No third-party libraries required; use Python standard library only.

## Sample Input 1

The following represents an MBR with:
- Entry 1: bootable, type 0x83 (Linux), LBA start=2048, LBA size=204800
- Entry 2: not bootable, type 0x82 (swap), LBA start=206848, LBA size=8192
- Entries 3 and 4: empty

```
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 80 fe ff ff 83
fe ff ff 00 08 00 00 00 20 03 00 00 fe ff ff 82
fe ff ff 00 1a 03 00 00 20 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 aa
```

Note: the above is formatted for readability; actual stdin is a single line. The solution code below handles it correctly.

## Sample Output 1

```
Partition 1: Bootable=Yes Type=0x83 LBAStart=2048 LBASize=204800
Partition 2: Bootable=No Type=0x82 LBAStart=206848 LBASize=8192
```

## Solution (Python)

```python
import sys

def parse_mbr(data: bytes):
    if data[510] != 0x55 or data[511] != 0xAA:
        print("Invalid MBR signature")
        return

    PARTITION_TABLE_OFFSET = 446
    ENTRY_SIZE = 16

    for i in range(4):
        offset = PARTITION_TABLE_OFFSET + i * ENTRY_SIZE
        entry = data[offset:offset + ENTRY_SIZE]

        status    = entry[0]
        part_type = entry[4]
        lba_start = int.from_bytes(entry[8:12], 'little')
        lba_size  = int.from_bytes(entry[12:16], 'little')

        if lba_start == 0 and lba_size == 0:
            continue

        bootable = "Yes" if status == 0x80 else "No"
        print(f"Partition {i+1}: Bootable={bootable} Type=0x{part_type:02X} LBAStart={lba_start} LBASize={lba_size}")

def main():
    raw = sys.stdin.read().split()
    data = bytes(int(b, 16) for b in raw)
    parse_mbr(data)

if __name__ == "__main__":
    main()
```
