# Prompt: Simulate a DMA Block Transfer

## Problem Description

Implement a simplified DMA block transfer simulator. The DMA copies data from a source memory region to a destination region in fixed-size beats. Print each beat as it is copied, then print the final destination region contents.

## Input Format

Exactly 6 lines, in this order:

```
MEM_SIZE <size>
SRC_ADDR <addr>
DST_ADDR <addr>
LENGTH <n>
BEAT_SIZE <b>
FILL <start_val>
```

- `MEM_SIZE` — total memory size in bytes (16 ≤ size ≤ 4096)
- `SRC_ADDR` — source start address (0-based byte index)
- `DST_ADDR` — destination start address (0-based byte index)
- `LENGTH` — number of bytes to transfer (multiple of BEAT_SIZE)
- `BEAT_SIZE` — bytes per DMA beat (1, 2, or 4)
- `FILL start_val` — source region is pre-filled: `memory[SRC_ADDR + i] = (start_val + i) % 256` for i in 0..LENGTH-1

## Output Format

For each beat (beats are numbered 1, 2, 3, ...):
```
Beat <n>: copied <beat_size> bytes from 0x<src_hex> to 0x<dst_hex> value=<hex_bytes>
```

- `<src_hex>` and `<dst_hex>` are 8-digit zero-padded lowercase hex addresses (e.g., `0x00000004`)
- `<hex_bytes>` are the transferred bytes as space-separated two-digit lowercase hex values (e.g., `0a 1b 2c 3d`)

After all beats, print the destination region:
```
DST[<decimal_addr>]: <hex_bytes_of_full_region>
```

- `<decimal_addr>` is the DST_ADDR as a decimal integer
- `<hex_bytes_of_full_region>` are all LENGTH destination bytes as space-separated two-digit lowercase hex

## Constraints

- SRC_ADDR + LENGTH <= MEM_SIZE
- DST_ADDR + LENGTH <= MEM_SIZE
- LENGTH is a positive multiple of BEAT_SIZE
- Source and destination regions do not overlap
- No libraries beyond the Python standard library
- Time limit: 3000 ms. Memory limit: 256 MB.

## Sample Test Cases

### Sample 1

Input:
```
MEM_SIZE 64
SRC_ADDR 0
DST_ADDR 32
LENGTH 8
BEAT_SIZE 4
FILL 10
```

Expected output:
```
Beat 1: copied 4 bytes from 0x00000000 to 0x00000020 value=0a 0b 0c 0d
Beat 2: copied 4 bytes from 0x00000004 to 0x00000024 value=0e 0f 10 11
DST[32]: 0a 0b 0c 0d 0e 0f 10 11
```

### Sample 2

Input:
```
MEM_SIZE 32
SRC_ADDR 0
DST_ADDR 16
LENGTH 4
BEAT_SIZE 1
FILL 0
```

Expected output:
```
Beat 1: copied 1 bytes from 0x00000000 to 0x00000010 value=00
Beat 2: copied 1 bytes from 0x00000001 to 0x00000011 value=01
Beat 3: copied 1 bytes from 0x00000002 to 0x00000012 value=02
Beat 4: copied 1 bytes from 0x00000003 to 0x00000013 value=03
DST[16]: 00 01 02 03
```

### Sample 3

Input:
```
MEM_SIZE 128
SRC_ADDR 4
DST_ADDR 64
LENGTH 6
BEAT_SIZE 2
FILL 250
```

Expected output:
```
Beat 1: copied 2 bytes from 0x00000004 to 0x00000040 value=fa fb
Beat 2: copied 2 bytes from 0x00000006 to 0x00000042 value=fc fd
Beat 3: copied 2 bytes from 0x00000008 to 0x00000044 value=fe ff
DST[64]: fa fb fc fd fe ff
```

### Sample 4 (hidden)

Input:
```
MEM_SIZE 256
SRC_ADDR 0
DST_ADDR 128
LENGTH 8
BEAT_SIZE 4
FILL 255
```

Expected output:
```
Beat 1: copied 4 bytes from 0x00000000 to 0x00000080 value=ff 00 01 02
Beat 2: copied 4 bytes from 0x00000004 to 0x00000084 value=03 04 05 06
DST[128]: ff 00 01 02 03 04 05 06
```
