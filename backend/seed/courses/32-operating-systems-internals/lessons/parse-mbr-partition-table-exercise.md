# Exercise: Parse an MBR Partition Table From Raw Bytes

The Master Boot Record encodes a partition table in a compact binary format — 4 entries of exactly 16 bytes each, starting at byte offset 446. In this exercise you will write a Python program that reads a sequence of raw bytes representing an MBR (given as hex pairs on stdin) and prints a human-readable partition table.

## What You Will Implement

Your program reads 512 bytes encoded as space-separated hex pairs (e.g., `00 00 ... 55 AA`) from stdin. It then:

1. Validates the boot signature (`0x55 0xAA` at offsets 510–511)
2. Parses all 4 partition table entries starting at offset 446
3. For each entry, prints: entry number, bootable flag, partition type, LBA start, and LBA size (in sectors)
4. Skips (does not print) entries where both `lba_start` and `lba_size` are zero (empty slots)

This mirrors real-world forensic and OS work where you inspect raw disk images to understand the partition layout without relying on high-level tools.

## Key Concepts Reinforced

- MBR binary layout and offsets (from the "Boot Stages" lesson)
- Little-endian 32-bit integer parsing in Python (`int.from_bytes(..., 'little')`)
- Recognizing well-known partition type codes (0x83 = Linux, 0x82 = swap, 0x0B/0x0C = FAT32, 0x05/0x0F = extended)
- Validating disk structures before trusting their contents

## Input / Output Format

See the companion prompt file `os-parse-mbr-partition-table-exercise.prompt.md` for the exact specification, constraints, and sample test cases.

## Starter Code

```python
import sys

def parse_mbr(data: bytes):
    # Validate boot signature
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

        # TODO: skip empty entries
        # TODO: print formatted output
        pass

def main():
    raw = sys.stdin.read().split()
    data = bytes(int(b, 16) for b in raw)
    parse_mbr(data)

if __name__ == "__main__":
    main()
```

## Tips

- Use Python's `struct.unpack_from('<I', data, offset)` or `int.from_bytes(slice, 'little')` — both work for little-endian 32-bit fields.
- The `status` byte is `0x80` for a bootable (active) partition and `0x00` for non-bootable.
- Print `Yes` or `No` for the bootable flag.
- Print partition type as a two-digit hex string prefixed with `0x` (e.g., `0x83`).
