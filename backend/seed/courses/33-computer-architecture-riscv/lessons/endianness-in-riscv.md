# Endianness in RISC-V

RISC-V is primarily a **little-endian** architecture. Its base ISA specification requires that all standard memory accesses use little-endian byte ordering. This aligns RISC-V with the dominant modern convention used by x86, ARM, and most embedded controllers.

## Default Little-Endian Behavior

When a RISC-V core executes a load or store instruction, it interprets memory in little-endian order:

```asm
# Store the 32-bit value 0x12345678 to address stored in a0
li   a1, 0x12345678
sw   a1, 0(a0)        # Stores bytes: 0x78 at a0+0, 0x56 at a0+1,
                      #               0x34 at a0+2, 0x12 at a0+3
```

A subsequent `lb` (load byte) from the base address returns `0x78` — the least significant byte — confirming little-endian layout.

## The "B" Extension for Big-Endian Support

The RISC-V privileged architecture specification does define a mechanism to support big-endian operation through the `mstatus.MBE`, `mstatus.SBE`, and `mstatus.UBE` fields (Machine/Supervisor/User Byte-Enable), which can flip the byte order for memory accesses at each privilege level.

However:
- This extension is **optional** and rarely implemented in real silicon.
- Nearly all RISC-V cores (SiFive, VexRiscv, CVA6, the Berkeley Rocket core) operate little-endian exclusively.
- The RISC-V Linux ABI and all standard toolchains assume little-endian.

## Load and Store Instructions vs Byte Order

RISC-V provides naturally-sized load and store variants:

| Instruction | Width  | Signed? | Notes                      |
|-------------|--------|---------|----------------------------|
| `lb`        | 8-bit  | Yes     | Sign-extends to XLEN       |
| `lbu`       | 8-bit  | No      | Zero-extends               |
| `lh`        | 16-bit | Yes     | Reads 2 bytes, little-endian |
| `lhu`       | 16-bit | No      |                             |
| `lw`        | 32-bit | Yes     | Reads 4 bytes, little-endian |
| `lwu`       | 32-bit | No      | RV64 only                  |
| `ld`        | 64-bit | –       | RV64 only                  |

There are no big-endian variants of these instructions in the standard ISA. If you need to read a big-endian value from a byte buffer (e.g., a network packet), you must read the bytes individually and reconstruct the integer with shifts:

```asm
# Read a 16-bit big-endian value from address in a0 into a1
lbu  a1, 0(a0)        # a1 = high byte
lbu  a2, 1(a0)        # a2 = low byte
slli a1, a1, 8        # shift high byte up
or   a1, a1, a2       # combine: a1 = big-endian 16-bit value
```

## Alignment Requirements in RISC-V

The base RISC-V ISA requires **naturally-aligned** accesses. An unaligned load or store:
- Raises an **address-misaligned exception** on a minimal hardware implementation.
- May be handled transparently by the hardware on cores that implement the unaligned access extension.
- Can be trapped and emulated by the OS kernel (at significant performance cost).

The `Zicbo` (Cache-Block Operations) and `Zam` (Misaligned Atomics) extensions relax some of these restrictions, but the safest practice is to keep all multi-byte accesses aligned.

## Practical Impact for C Programmers on RISC-V

```c
// This code is correct and efficient on RISC-V
uint32_t read_u32_le(const uint8_t *p) {
    uint32_t v;
    memcpy(&v, p, 4);   // compiler generates a single 'lw' when p is aligned
    return v;
}

// This is portable for a big-endian field (e.g., from a network packet)
uint32_t read_u32_be(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
         | ((uint32_t)p[2] <<  8) |  (uint32_t)p[3];
}
```

Using `memcpy` rather than a pointer cast avoids undefined behavior from strict aliasing and lets the compiler emit the optimal `lw` instruction on RISC-V.

## Summary

- RISC-V is **little-endian by default** in all practical implementations.
- Big-endian support is an optional extension in the privileged spec but almost never deployed.
- There are no big-endian load/store instructions; big-endian values from external sources must be reconstructed manually.
- Alignment is required by the base ISA; misaligned accesses trap unless the hardware or OS handles them.

> **Interview answer:** RISC-V is little-endian by default. The privileged spec allows optional big-endian modes via `mstatus.MBE/SBE/UBE`, but real implementations almost always use little-endian. There are no big-endian load/store instructions; parsing big-endian binary data requires byte-by-byte reads reassembled with shifts.
