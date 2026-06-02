# Volatile vs Non-Volatile Memory

Memory is classified by what happens when you cut power. **Volatile** memory loses its contents when power is removed. **Non-volatile** memory retains data indefinitely without power. This distinction determines where in a system each technology is used and what guarantees software can make about data persistence.

## Volatile Memory

Volatile memory requires a continuous power supply to maintain its stored state.

### SRAM (Static RAM)
- Holds state via cross-coupled transistor latches
- Loses data immediately on power loss
- Used for: CPU caches, register files, TLBs
- Special case: **SRAM with battery backup** (used in some real-time clocks and early game cartridges) provides persistence at the cost of a battery

### DRAM (Dynamic RAM)
- Stores each bit as charge on a capacitor
- Charge dissipates within milliseconds without refresh
- Loses data on power loss or if refresh is interrupted
- Used for: main memory (RAM modules), GPU frame buffers

### CPU Registers
- Implemented as flip-flops — the most volatile storage in the system
- Content is lost on any context switch unless saved to the stack by the OS

## Non-Volatile Memory

Non-volatile memory retains data without power, making it suitable for persistent storage.

### Flash Memory (NAND / NOR)
Flash stores charge in a **floating-gate transistor**. Charge is trapped without power, enabling persistence.

| Type | Cell type | Read | Write | Use case |
|------|-----------|------|-------|----------|
| SLC NAND | 1 bit/cell | Fast | Medium | Enterprise SSDs, embedded |
| MLC NAND | 2 bits/cell | Medium | Slower | Consumer SSDs |
| TLC NAND | 3 bits/cell | Slower | Slow | High-capacity SSDs |
| QLC NAND | 4 bits/cell | Slowest | Slowest | Archive SSDs |
| NOR Flash | 1 bit/cell | Very fast (byte-random) | Slow | Firmware, bootloaders |

Flash has a critical limitation: cells wear out after a finite number of **program-erase (P/E) cycles** (typically 1,000–100,000 cycles depending on type). SSDs use **wear leveling** to distribute writes evenly across blocks.

### Magnetic Hard Disk (HDD)
- Data stored as magnetic polarity on a spinning platter — survives power loss indefinitely
- Mechanical seek introduces millisecond-scale latency
- High capacity, low cost per GB
- Susceptible to physical shock (moving parts)

### Emerging Non-Volatile Technologies

| Technology | Full name | Key property |
|-----------|-----------|-------------|
| NVDIMM | Non-Volatile DIMM | DRAM + flash + supercapacitor on a DIMM module |
| PCM | Phase-Change Memory | Uses material phase (crystalline vs amorphous) |
| STT-MRAM | Spin-Transfer Torque MRAM | Uses magnetic tunnel junctions; fast writes |
| 3D XPoint / Optane | Intel/Micron | ~10× denser than DRAM, ~1000× faster than NAND |

## The Volatile/Non-Volatile Boundary in System Design

The boundary between volatile and non-volatile storage has major implications for system design:

```
Power failure
    │
    ▼
CPU Registers ──→ LOST
SRAM Cache   ──→ LOST
DRAM RAM     ──→ LOST
────────────────────── volatile/non-volatile boundary
SSD / HDD    ──→ SAFE
Flash ROM    ──→ SAFE
```

**Write-ahead logging (WAL):** Databases ensure durability by writing changes to persistent storage (a log) before confirming a commit. The log entry is fsync'd to disk — crossing the volatile/non-volatile boundary — before the user receives a success response.

**NVDIMM / persistent memory:** Emerging byte-addressable non-volatile memory (like Intel Optane DC) sits in DRAM slots but survives power loss. This blurs the boundary and requires new programming models (pmdk, DAX mode).

## Persistence Guarantees and the OS

The OS kernel maintains a **page cache** (volatile DRAM) that buffers disk writes. A `write()` syscall places data in the page cache; it is not on disk until the page is flushed. Calling `fsync()` forces a flush, ensuring the data crosses the volatile boundary.

```c
int fd = open("data.bin", O_WRONLY);
write(fd, buf, len);  // data is in volatile page cache — NOT persistent yet
fsync(fd);            // forces flush to non-volatile storage — NOW persistent
close(fd);
```

Failing to call `fsync()` before a crash is a common source of data loss bugs.

## Common Pitfalls

- **Assuming RAM is persistent:** Rebooting or crashing loses all RAM contents. Programs must save important state to disk.
- **Flash write amplification:** SSDs must erase a full 128 KB–4 MB block before writing — a 4 KB write can trigger a 4 MB erase/rewrite cycle internally.
- **Not calling fsync():** OS page cache provides the illusion of persistence until a crash reveals otherwise.
- **Confusing NOR and NAND flash:** NOR flash supports byte-random reads and is used for firmware (BIOS, bootloaders); NAND flash is block-oriented and used for mass storage.

> **Interview answer:** Volatile memory (SRAM, DRAM) loses data on power loss and is used for fast temporary storage; non-volatile memory (flash, HDD) retains data without power and is used for persistent storage — the boundary between them is where databases use fsync to guarantee durability.
