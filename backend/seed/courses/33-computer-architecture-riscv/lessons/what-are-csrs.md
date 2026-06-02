# What Are Control and Status Registers?

Control and Status Registers (CSRs) are a dedicated set of registers in RISC-V that sit outside the standard integer register file (x0–x31). They control the processor's operating mode, record information about exceptions and interrupts, and expose hardware capabilities to software.

## Why CSRs Exist

General-purpose registers hold data for computation. CSRs hold **machine state** — things like:

- Which privilege level is currently active
- Whether interrupts are globally enabled
- The address to jump to when a trap occurs
- The cause of the most recent exception

Separating this state into dedicated registers keeps the integer register file clean and lets the hardware enforce access-control rules: some CSRs are only readable or writable at machine mode (M-mode), the highest privilege level.

## The CSR Address Space

RISC-V reserves a 12-bit address space for CSRs, giving up to 4096 registers. The top four bits encode both the privilege level required to access the register and whether it is read-only or read-write:

| Bits [11:10] | Access    | Bits [9:8] | Min privilege |
|--------------|-----------|------------|---------------|
| 00, 01, 10   | Read-write | 00        | User          |
| 11           | Read-only  | 01        | Supervisor    |
|              |            | 10        | Hypervisor    |
|              |            | 11        | Machine       |

Attempting to write a read-only CSR, or accessing a CSR at a privilege level lower than required, raises an **illegal instruction exception**.

## Key M-mode CSRs at a Glance

| CSR name | Address | Role |
|----------|---------|------|
| `mstatus` | 0x300 | Global interrupt enable, privilege tracking |
| `misa`    | 0x301 | ISA extensions implemented |
| `mie`     | 0x304 | Interrupt enable bits per source |
| `mtvec`   | 0x305 | Trap-handler base address |
| `mepc`    | 0x341 | PC saved when a trap occurs |
| `mcause`  | 0x342 | Cause code for the trap |
| `mtval`   | 0x343 | Fault address or instruction word |
| `mip`     | 0x344 | Interrupt pending bits |

## CSRs and the Trap Flow

When an exception or interrupt fires, the hardware performs several atomic steps before the first instruction of the trap handler executes:

1. The faulting PC is saved in `mepc`.
2. The cause code is written to `mcause`.
3. Fault-specific detail (e.g., bad address) is written to `mtval`.
4. `mstatus.MIE` (global interrupt enable) is copied to `mstatus.MPIE` and then cleared.
5. The previous privilege level is saved in `mstatus.MPP`.
6. The PC is set to the address in `mtvec`.

Returning from a trap with `MRET` reverses steps 4–6 and jumps back to `mepc`.

## Reading and Writing CSRs

CSRs are accessed with a dedicated family of instructions (`CSRRW`, `CSRRS`, `CSRRC`, and their immediate variants). Normal load/store instructions cannot touch CSRs. This design lets the hardware guarantee atomicity: a single CSR instruction can read the old value and write the new value in one operation.

```asm
csrr  t0, mcause    # read mcause into t0 (pseudo: csrrs t0, mcause, x0)
csrw  mtvec, t1     # write t1 into mtvec (pseudo: csrrw x0, mtvec, t1)
```

## Common Pitfalls

- **Forgetting privilege level**: user-mode code cannot read most M-mode CSRs. The attempt traps immediately.
- **Treating CSRs as memory**: you cannot use `lw`/`sw` on CSR addresses. Use `csrr`/`csrw` or their variants.
- **Stale mepc on nested traps**: if a handler takes another trap before saving `mepc`, the original value is lost. Always save it early.

> **Interview answer:** CSRs are a separate 4096-entry register file in RISC-V that store machine control state such as interrupt enable bits, trap handler addresses, and trap cause codes. They are accessed exclusively through CSR instructions and are protected by privilege-level encoding in their 12-bit address.
