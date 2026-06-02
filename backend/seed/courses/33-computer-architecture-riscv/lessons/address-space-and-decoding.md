# Address Space and Address Decoding

The CPU sees a single, flat **address space** — a numbered range of locations it can read from or write to. In reality, that range is split among RAM, ROM, memory-mapped I/O registers, and other devices. **Address decoding** is the hardware logic that maps each address to exactly one device.

## What Is an Address Space?

For a CPU with an N-bit address bus, the address space spans 2^N distinct locations. A 32-bit address bus gives 4 GiB (2^32 = 4,294,967,296 bytes). A 64-bit bus gives 16 EiB — far more than any current system physically populates.

The address space is divided into **regions**, each assigned to one device:

```
0x0000_0000 – 0x0FFF_FFFF   256 MiB  DRAM
0x1000_0000 – 0x1000_0FFF     4 KiB  Boot ROM
0x2000_0000 – 0x2000_0FFF     4 KiB  GPIO registers
0x2000_1000 – 0x2000_1FFF     4 KiB  UART registers
0xFFFF_0000 – 0xFFFF_FFFF    64 KiB  On-chip SRAM
```

Any address that falls outside every defined region is **unmapped**. Accessing an unmapped address typically causes a bus error or fault exception.

## Address Decoding

Each device has a **decoder** — combinational logic that asserts a chip-select (CS) signal when the address bus value falls within that device's assigned range.

### Full Decoding

Every address line participates in the decode. The device responds to exactly one contiguous range and no other.

```
// Device at 0x2000_0000–0x2000_0FFF (4 KiB)
CS = (ADDR[31:12] == 20'h20000)   // top 20 bits fixed
     && MREQ                       // memory cycle active
```

Full decoding is safe and unambiguous — no address maps to two devices.

### Partial Decoding

Only the most significant address lines are decoded; some lines are ignored. This is cheaper (fewer gates) but creates **address aliasing** — the device responds to multiple address ranges.

```
// Partial decode: only bits [31:16] checked
CS = (ADDR[31:16] == 16'h2000)
// Device appears at 0x2000_0000, 0x2000_1000, ..., 0x2000_F000
```

Aliasing is acceptable in simple embedded systems where only one device occupies a large block, but dangerous in complex systems.

## Memory-Mapped I/O (MMIO)

RISC-V and most modern ISAs use **memory-mapped I/O** — peripheral control registers live in the same address space as RAM. The CPU uses ordinary load/store instructions to read from or write to a UART, GPIO, or timer.

```asm
# RISC-V: write 0x41 ('A') to UART TX register at 0x10000000
li   t0, 0x10000000    # load UART base address
li   t1, 0x41          # character 'A'
sb   t1, 0(t0)         # store byte to UART TX
```

The alternative, **port-mapped I/O** (used by x86), dedicates separate `IN`/`OUT` instructions to a distinct I/O address space. RISC-V has no separate I/O space — everything is MMIO.

## Address Decoding in RISC-V SoCs

In a RISC-V SoC built with Rocket Chip or Chipyard, address regions are defined in a **device tree** or **platform description**. The interconnect (TileLink crossbar) performs the decoding internally:

```
// Chipyard AddressSet (Scala-like pseudocode)
val uart = LazyModule(new TLUART(AddressSet(0x54000000, 0xFFF)))
// → UART responds to 0x54000000–0x54000FFF
```

The `AddressSet` specifies a base address and a mask. The crossbar routes any transaction whose address matches to the correct slave port.

## Worked Example: Decoding a 4-Device System

Given a 16-bit address bus, divide the 64 KiB space among four devices:

| Device | Range | Top 2 bits | CS logic |
|--------|-------|-----------|----------|
| RAM    | 0x0000–0x3FFF | 00 | A15=0, A14=0 |
| ROM    | 0x4000–0x7FFF | 01 | A15=0, A14=1 |
| UART   | 0x8000–0xBFFF | 10 | A15=1, A14=0 |
| GPIO   | 0xC000–0xFFFF | 11 | A15=1, A14=1 |

Only 2 bits are decoded — this is partial decoding, but with only four devices it maps cleanly.

## Common Pitfalls

- **Overlapping regions** — two decoders both assert CS for the same address causes a bus fight.
- **Cache coherence with MMIO** — caching MMIO addresses is almost always wrong. Mark MMIO regions as non-cacheable in the page tables or memory attribute registers.
- **Endianness mismatch** — when a 32-bit peripheral register is accessed byte-by-byte, the byte order matters. RISC-V is little-endian by default.

**Interview answer:** Address decoding is the combinational logic that asserts a chip-select when the bus address falls within a device's assigned range, partitioning the CPU's flat address space among RAM, ROM, and memory-mapped peripheral registers.
