# mtval, misa, and Other Key CSRs

Beyond the five core trap-handling CSRs, several other M-mode registers provide fault details, hardware capability discovery, and performance monitoring. This lesson covers `mtval`, `misa`, `mvendorid`, `marchid`, `mhartid`, `mcycle`, and `minstret`.

## mtval — Machine Trap Value (CSR 0x343)

`mtval` provides additional context about the trap. Its meaning depends on `mcause`:

| Exception | mtval content |
|-----------|---------------|
| Instruction address misaligned | Faulting instruction address |
| Instruction access fault | Faulting instruction address |
| Illegal instruction | Faulting instruction word (or 0) |
| Breakpoint (EBREAK) | Address of the EBREAK instruction |
| Load/Store misaligned | Faulting virtual address |
| Load/Store access fault | Faulting virtual address |
| Load/Store page fault | Faulting virtual address |
| Environment call (ecall) | 0 (undefined by spec) |

For interrupts, `mtval` is 0 (or an implementation-defined value — never rely on it for interrupts).

### Using mtval in an Access-Fault Handler

```c
uintptr_t fault_addr = read_csr(mtval);
uintptr_t cause      = read_csr(mcause) & 0x3F;

if (cause == 13) {  // load page fault
    printf("Load page fault at address 0x%lx\n", fault_addr);
    // map the page, then retry (return to mepc unchanged)
}
```

## misa — Machine ISA Register (CSR 0x301)

`misa` describes the ISA extensions implemented by the hart:

```
 XLEN-1 XLEN-2        25 24              0
 ┌────┬──┬────────────────┬──────────────┐
 │ MXL │   (zero)         │   Extensions │
 └────┴──┴────────────────┴──────────────┘
```

- **MXL** (bits [XLEN-1:XLEN-2]): base ISA width — 1=RV32, 2=RV64, 3=RV128.
- **Extensions** (bits [25:0]): each bit corresponds to a letter A–Z. Bit 0 = A (atomics), bit 2 = C (compressed), bit 3 = D (double FP), bit 8 = I (base integer), bit 12 = M (multiply/divide), etc.

```c
uintptr_t isa = read_csr(misa);
int mxl = isa >> (sizeof(uintptr_t)*8 - 2);  // 1 or 2
bool has_C = (isa >> 2) & 1;   // C extension present?
bool has_M = (isa >> 12) & 1;  // M extension present?
```

`misa` may be read-only on some implementations. Writing to it on such hardware is silently ignored (no exception).

## mvendorid, marchid, mimpid — Identity Registers

| CSR | Address | Content |
|-----|---------|---------|
| `mvendorid` | 0xF11 | JEDEC vendor ID (0 = non-commercial) |
| `marchid`   | 0xF12 | Microarchitecture ID (allocated by RISC-V Foundation) |
| `mimpid`    | 0xF13 | Implementation version (vendor-defined) |

All three are read-only. They allow firmware to identify the silicon without probing behavior.

## mhartid — Hardware Thread ID (CSR 0xF14)

In multi-core systems, each hart (hardware thread) has a unique non-negative integer ID. Hart 0 is required to be present. Software uses `mhartid` to:

- Select per-hart stacks and data structures at boot.
- Implement spinlocks where only hart 0 performs certain initialization.

```asm
csrr  t0, mhartid
bnez  t0, secondary_hart_entry   # hart 0 continues here
```

## mcycle and minstret — Performance Counters (CSR 0xB00, 0xB02)

- `mcycle`: counts clock cycles elapsed since reset (or last write).
- `minstret`: counts instructions retired since reset (or last write).

Both are 64-bit counters even on RV32, where they are split into `mcycle`/`mcycleh` and `minstret`/`minstreth` (high word at addresses 0xB80/0xB82).

```asm
# Measure cycle count of a loop (RV64)
csrr   t0, mcycle
# ... code to measure ...
csrr   t1, mcycle
sub    t2, t1, t0    # t2 = elapsed cycles
```

## mscratch — Machine Scratch Register (CSR 0x340)

`mscratch` is a general-purpose register the hardware does not interpret. Its canonical use is to hold the address of a per-hart save area during trap entry, before the handler has a safe register to use:

```asm
trap_entry:
    csrrw  t0, mscratch, t0    # swap t0 with mscratch (mscratch = old t0, t0 = save area ptr)
    sw     t1, 0(t0)           # now t0 points to the save area
    sw     a0, 4(t0)
    # ... save all registers using t0 as base ...
```

This pattern avoids clobbering any register before it is saved.

## Common Pitfalls

- **Relying on mtval for interrupts**: the spec says mtval is 0 for interrupts, but some implementations write arbitrary values. Always gate on `mcause` first.
- **Assuming misa is writable**: many production cores make it read-only. Write once, check the readback.
- **Reading mcycle on RV32 without handling carry**: the high word (`mcycleh`) may increment between two reads of the low word. Use the standard double-read idiom:

```asm
read_cycle64:
    csrr  t1, mcycleh
    csrr  t0, mcycle
    csrr  t2, mcycleh
    bne   t1, t2, read_cycle64  # retry if carry happened between reads
```

> **Interview answer:** `mtval` provides trap-specific detail such as the faulting address or instruction word. `misa` encodes the supported ISA extensions in a 26-bit field plus a 2-bit base-width indicator. `mscratch` is a free register conventionally used to hold a pointer to per-hart saved-register storage during trap entry.
