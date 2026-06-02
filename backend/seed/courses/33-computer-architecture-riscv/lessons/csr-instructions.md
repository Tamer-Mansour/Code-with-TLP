# CSR Instructions: CSRRW, CSRRS, CSRRC

RISC-V provides six CSR instructions — three register-source variants and three immediate-source variants. Every read or write to any CSR must go through one of these instructions; there is no memory-mapped alias for the CSR file.

## The Core Three

### CSRRW — Atomic Read/Write

```
CSRRW rd, csr, rs1
```

- Reads the current value of `csr` into `rd`.
- Writes `rs1` into `csr`.
- Both happen atomically in a single cycle.

If `rd` is `x0`, the hardware skips the read step entirely (no side effects from reading).

### CSRRS — Atomic Read and Set Bits

```
CSRRS rd, csr, rs1
```

- Reads the current value of `csr` into `rd`.
- Performs a bitwise OR: `csr = csr | rs1`.
- Sets whichever bits are 1 in `rs1`; leaves 0-bits unchanged.

If `rs1` is `x0`, this becomes a **pure read** with no write side effect.

### CSRRC — Atomic Read and Clear Bits

```
CSRRC rd, csr, rs1
```

- Reads the current value of `csr` into `rd`.
- Performs a bit-clear: `csr = csr & ~rs1`.
- Clears whichever bits are 1 in `rs1`; leaves 0-bits unchanged.

If `rs1` is `x0`, this is again a pure read.

## Immediate Variants

Each instruction has a `*I` twin that uses a 5-bit zero-extended unsigned immediate instead of `rs1`:

| Instruction | Operation                          |
|-------------|-------------------------------------|
| `CSRRWI`   | `rd = csr; csr = uimm[4:0]`         |
| `CSRRSI`   | `rd = csr; csr = csr \| uimm[4:0]`  |
| `CSRRCI`   | `rd = csr; csr = csr & ~uimm[4:0]` |

The immediate is unsigned and zero-extended to XLEN bits. Use the immediate form when the mask fits in 5 bits, saving the need to load a constant into a register.

## Assembler Pseudo-Instructions

The assembler provides convenient aliases:

```asm
csrr  rd, csr        # Read:  CSRRS rd, csr, x0
csrw  csr, rs        # Write: CSRRW x0, csr, rs
csrs  csr, rs        # Set:   CSRRS x0, csr, rs
csrc  csr, rs        # Clear: CSRRC x0, csr, rs
csrwi csr, imm       # Write immediate
csrsi csr, imm       # Set bits by immediate
csrci csr, imm       # Clear bits by immediate
```

## Worked Example: Enabling Machine-Mode Timer Interrupts

Bit 7 of `mie` (`MTIE`) enables the machine-mode timer interrupt. To set it without disturbing other bits:

```asm
li    t0, (1 << 7)   # MTIE mask = 0x80
csrs  mie, t0        # mie |= 0x80  — set MTIE only
```

To disable it later:

```asm
li    t0, (1 << 7)
csrc  mie, t0        # mie &= ~0x80  — clear MTIE only
```

To atomically swap the entire `mstatus` value and see the old one:

```asm
csrrw t1, mstatus, t0   # t1 = old mstatus; mstatus = t0
```

## Side Effects and Read-Only CSRs

Some CSRs (address bits [11:10] == 11) are read-only. Attempting a write raises an **illegal instruction exception** regardless of privilege level. Always check the spec before writing to an unfamiliar CSR.

Reads themselves can also have side effects on certain hardware-defined performance counters (e.g., reading `mcycle` latches a snapshot). These cases are rare but documented in the RISC-V privileged spec.

## Common Pitfalls

- **CSRRW with rd=x0 skips the read** but still performs the write — useful for write-only semantics.
- **CSRRS/CSRRC with rs1=x0 skip the write** — the canonical pure-read form. Never use CSRRW with rs1=x0 as a read; it zeros the CSR.
- **5-bit limit on immediates**: immediates larger than 31 require loading into a register first.

> **Interview answer:** CSRRW atomically reads a CSR and replaces it; CSRRS reads and sets bits via OR; CSRRC reads and clears bits via AND-NOT. Each has an immediate variant. Using x0 as destination suppresses the read, and using x0 as source suppresses the write — enabling pure write or pure read semantics.
