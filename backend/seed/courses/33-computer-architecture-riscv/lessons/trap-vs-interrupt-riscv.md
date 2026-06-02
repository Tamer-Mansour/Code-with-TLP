# Traps vs Interrupts in RISC-V

RISC-V documentation uses "trap" as the umbrella term for any control-flow hijack caused by the hardware. Under that umbrella sit two fundamentally different phenomena — **exceptions** and **interrupts** — and understanding the distinction is critical for writing correct handlers.

## Unified Terminology

| RISC-V Term | Meaning |
|---|---|
| **Trap** | Any event that transfers control to a handler (supertype) |
| **Exception** | Trap caused by the currently executing instruction (synchronous) |
| **Interrupt** | Trap caused by an event external to the instruction stream (asynchronous) |

The spec also uses "fault" informally for exceptions that may be retried, and "abort" for unrecoverable hardware errors — but these are not formal ISA categories.

## Synchronous vs Asynchronous

The most important practical difference is **timing**:

- An **exception** is fully reproducible. Run the same instruction stream with the same state and you get the same exception at the same PC. The faulting instruction is pointed to by `mepc` (or, for some architectures, `mepc` points one instruction past it — RISC-V saves the address **of** the faulting instruction).
- An **interrupt** can arrive between any two instructions. `mepc` contains the PC of the **next instruction that would have executed**, not of any faulting instruction.

This means interrupt return simply restores `mepc` unchanged, while exception return often needs to advance `mepc` by 4 (or re-execute the instruction after fixing the cause).

## Reading mcause

The `mcause` CSR encodes both type and specific cause in a single XLEN-bit register:

```
 XLEN-1      XLEN-2 ... 0
┌──────────┬─────────────────┐
│ Interrupt│  Exception Code │
│  bit (I) │                 │
└──────────┴─────────────────┘
```

- **I = 1** → interrupt; the code identifies which interrupt source.
- **I = 0** → exception; the code identifies which exception.

```asm
csrr  t0, mcause
bltz  t0, is_interrupt   # MSB set means interrupt
# else: it's an exception
```

### Common Exception Codes (I = 0)

| Code | Name |
|---|---|
| 0 | Instruction address misaligned |
| 2 | Illegal instruction |
| 3 | Breakpoint (ebreak) |
| 4 | Load address misaligned |
| 6 | Store address misaligned |
| 8 | Environment call from U-mode (ecall) |
| 11 | Environment call from M-mode (ecall) |
| 12 | Instruction page fault |
| 13 | Load page fault |
| 15 | Store page fault |

### Common Interrupt Codes (I = 1)

| Code | Name |
|---|---|
| 1 | Supervisor software interrupt |
| 3 | Machine software interrupt |
| 5 | Supervisor timer interrupt |
| 7 | Machine timer interrupt |
| 9 | Supervisor external interrupt |
| 11 | Machine external interrupt |

## The Role of mtval

`mtval` carries auxiliary information that varies by cause:

- **Page fault / misaligned access** — the faulting virtual address.
- **Illegal instruction** — the bad instruction word (if it fits).
- **Breakpoint** — the breakpoint address.
- **All others** — implementation-defined; software should not rely on it.

## Nested and Re-entrant Traps

RISC-V disables M-mode interrupts (`mstatus.MIE = 0`) on trap entry. This prevents interrupt nesting by default. To allow nested interrupts a handler must:

1. Save all caller-saved registers and the current CSR state.
2. Re-enable `mstatus.MIE`.
3. Restore everything before executing `mret`.

Exceptions can still arrive during interrupt handling regardless of `MIE` because exceptions are synchronous to the instruction stream — they cannot be masked.

## Worked Example: Identifying a Trap

```c
// C pseudo-code for a generic trap dispatcher
void trap_handler(void) {
    long cause = read_csr(mcause);
    if (cause < 0) {              // MSB set → interrupt
        handle_interrupt(cause & 0x7FFFFFFF);
    } else {                      // exception
        handle_exception(cause, read_csr(mepc), read_csr(mtval));
    }
}
```

> **Interview answer:** Exceptions are synchronous traps caused by a specific instruction (e.g., page fault, illegal opcode). Interrupts are asynchronous events from outside the instruction stream (e.g., timer, UART). Both set `mcause`; the MSB distinguishes them — 1 for interrupt, 0 for exception. The key behavioral difference: exception handlers often advance or re-execute `mepc`; interrupt handlers return to `mepc` as-is.

## Common Pitfalls

- Treating all traps as interrupts and skipping `mepc` advancement causes infinite exception loops.
- Forgetting that `ecall` is an **exception** (not an interrupt) — it is synchronous and code 8/9/10/11 depending on current privilege.
- Platform interrupts (external) go through the PLIC; the ISA only defines the signaling path, not the source enumeration.
