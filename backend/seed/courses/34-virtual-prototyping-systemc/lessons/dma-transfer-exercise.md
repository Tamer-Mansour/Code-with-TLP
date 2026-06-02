# Simulate a DMA Block Transfer

In this exercise you will implement a simplified DMA block transfer simulator in Python. The simulator models a DMA engine that copies data from a source memory region to a destination memory region in fixed-size beats, logging each beat and printing the final memory state.

## What You Will Implement

Your program will:
1. Initialize a flat memory array of a given size (bytes), filled with known values at the source region.
2. Execute a DMA block transfer from a source address to a destination address for a given length, in beats of a given width.
3. Print each beat's details as it is copied.
4. Print the contents of the destination region after the transfer.

## Input Format

```
MEM_SIZE <size>          # total memory size in bytes
SRC_ADDR <addr>          # source start address
DST_ADDR <addr>          # destination start address
LENGTH <n>               # number of bytes to transfer
BEAT_SIZE <b>            # bytes per beat (1, 2, or 4)
FILL <start_val>         # source memory is filled: src[i] = (start_val + i) % 256
```

## Output Format

For each beat print:
```
Beat <n>: copied <beat_size> bytes from 0x<src_hex> to 0x<dst_hex> value=<hex_bytes>
```

where `<hex_bytes>` is the transferred bytes as space-separated two-digit hex values (e.g., `0a 1b`).

After all beats, print the destination region as a hex dump:
```
DST[<addr>]: <hex_bytes_of_full_region>
```

`<hex_bytes_of_full_region>` is all LENGTH bytes of the destination, space-separated two-digit hex, starting from DST_ADDR.

## Example

Input:
```
MEM_SIZE 64
SRC_ADDR 0
DST_ADDR 32
LENGTH 8
BEAT_SIZE 4
FILL 10
```

Output:
```
Beat 1: copied 4 bytes from 0x00000000 to 0x00000020 value=0a 0b 0c 0d
Beat 2: copied 4 bytes from 0x00000004 to 0x00000024 value=0e 0f 10 11
DST[32]: 0a 0b 0c 0d 0e 0f 10 11
```

## Constraints

- `MEM_SIZE` is between 16 and 4096.
- `SRC_ADDR` + `LENGTH` <= `MEM_SIZE` (no overflow).
- `DST_ADDR` + `LENGTH` <= `MEM_SIZE` (no overflow).
- `LENGTH` is a multiple of `BEAT_SIZE`.
- `BEAT_SIZE` is 1, 2, or 4.
- Source and destination regions do not overlap.
- No external libraries required.
