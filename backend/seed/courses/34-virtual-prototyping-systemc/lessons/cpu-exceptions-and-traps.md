# Exceptions and Traps in a CPU Model

Exceptions — and the closely related concepts of interrupts, faults, and traps — are the mechanism through which a CPU transitions from normal code execution into privileged handler code. Implementing them correctly is one of the hardest parts of writing an ISS because they must interleave with every stage of the fetch-execute loop and interact with the privilege-level state machine.

## Terminology Aligned with RISC-V

Different ISAs use different terms. The RISC-V specification is precise:

| Term | Definition |
|---|---|
| **Exception** | An unusual condition arising from instruction execution (e.g., illegal instruction, misaligned load) |
| **Interrupt** | An external asynchronous event (e.g., timer, UART RX ready) |
| **Trap** | The unified mechanism by which control is transferred to the trap handler — covers both exceptions and interrupts |
| **Fault** | An exception that occurs before the faulting instruction completes (can be retried) |
| **Abort** | A fault that cannot be retried (e.g., double fault) |

In x86 terminology, "exception" covers all three of the above; in Arm, "exception" covers interrupts too. When modeling multi-architecture platforms, align your naming with the ISA spec you implement.

## What Must Be Saved on a Trap

When the CPU takes a trap, it must atomically:

1. Save the faulting (or interrupted) PC into the **exception program counter** register (`mepc` in RISC-V, `ELR_ELx` in Arm).
2. Save the cause code into the **cause** register (`mcause`/`scause`).
3. Save additional fault information into `mtval` (e.g., the bad address for a load fault).
4. Save the current privilege and interrupt-enable state into `mstatus`.
5. Jump to the trap vector (`mtvec`).

In an ISS, these are all just register-file writes:

```cpp
void RISCVCPU::take_exception(uint32_t cause, uint32_t tval) {
    csr[MEPC]    = pc;             // where to return after mret
    csr[MCAUSE]  = cause;          // reason code
    csr[MTVAL]   = tval;           // bad address or instruction word
    uint32_t mstatus = csr[MSTATUS];
    // Save current MIE into MPIE, clear MIE (disable interrupts)
    mstatus = (mstatus & ~MSTATUS_MPIE) | ((mstatus & MSTATUS_MIE) ? MSTATUS_MPIE : 0);
    mstatus &= ~MSTATUS_MIE;
    // Save current privilege into MPP (simplified: always M-mode here)
    csr[MSTATUS] = mstatus;
    pc = csr[MTVEC] & ~3UL;       // jump to handler (vectored mode omitted for brevity)
}
```

## The RISC-V Cause Codes

The `mcause` register encodes the trap source. The MSB (`cause[31]`) is 1 for interrupts, 0 for exceptions.

| mcause (interrupt=0) | Exception |
|---|---|
| 0 | Instruction address misaligned |
| 1 | Instruction access fault |
| 2 | Illegal instruction |
| 4 | Load address misaligned |
| 5 | Load access fault |
| 6 | Store/AMO address misaligned |
| 7 | Store/AMO access fault |
| 8–11 | Environment call (ecall) from U/S/H/M mode |

| mcause (interrupt=1) | Interrupt |
|---|---|
| 3 | Machine software interrupt |
| 7 | Machine timer interrupt |
| 11 | Machine external interrupt |

## Modeling Interrupt Delivery

Interrupt delivery in an ISS must be conditional on the interrupt-enable bit in `mstatus.MIE` and on the individual enable bits in `mie` (Machine Interrupt Enable):

```cpp
bool RISCVCPU::interrupts_enabled() const {
    return (csr[MSTATUS] & MSTATUS_MIE) != 0;
}

void RISCVCPU::check_and_take_interrupt() {
    uint32_t pending = csr[MIP] & csr[MIE]; // what is pending AND enabled?
    if (pending == 0 || !interrupts_enabled()) return;

    // Priority: MEI > MSI > MTI (simplified)
    uint32_t cause;
    if (pending & MIP_MEIP) cause = (1u << 31) | 11; // machine external
    else if (pending & MIP_MSIP) cause = (1u << 31) | 3;
    else cause = (1u << 31) | 7; // timer

    take_exception(cause, 0);
}
```

The `MIP` (Machine Interrupt Pending) register is updated by external signals arriving from peripherals. In a TLM platform, an interrupt controller (e.g., PLIC) writes to `MIP` via a CPU method call or a signal.

## The `mret` Return Instruction

Returning from a machine-mode trap uses `mret`, which reverses the state saved on trap entry:

```cpp
case MRET:
    // Restore MIE from MPIE, set MPIE to 1, restore privilege
    csr[MSTATUS] = (csr[MSTATUS] & ~MSTATUS_MIE)
                 | ((csr[MSTATUS] & MSTATUS_MPIE) ? MSTATUS_MIE : 0);
    csr[MSTATUS] |= MSTATUS_MPIE; // MPIE = 1 after mret
    pc = csr[MEPC];               // return to saved PC
    return;
```

## The `ecall` Trap

The `ECALL` instruction raises an environment-call exception. Its cause code depends on the current privilege level. This is how a U-mode program asks the OS for a service, and how S-mode asks the machine-mode firmware. In a bare-metal ISS that runs everything in M-mode, `ecall` typically triggers a halt or a custom semihosting handler:

```cpp
case ECALL:
    // In a bare-metal test environment, treat as exit
    if (reg[10] == 0) { halted = true; exit_code = 0; }
    else              { halted = true; exit_code = reg[10]; }
    return;
```

## Common Pitfalls

- **Not saving `pc` before executing the instruction**: For a fetch fault, `mepc` must point to the instruction that faulted, not the next one.
- **Infinite trap loop**: If the trap vector address itself is unmapped, taking the trap causes another fault. Add a guard in `take_exception()`.
- **Forgetting `mstatus.MPIE`**: Omitting the save/restore of MPIE means the OS cannot correctly re-enable interrupts after returning from a handler.
- **Nested interrupt confusion**: M-mode interrupts are masked once MIE is cleared. Some designs need to re-enable MIE inside the handler for preemptible interrupts — do not hardcode that behavior in the ISS.

## Interview Answer

> "When an exception or interrupt is taken, the ISS atomically saves the current PC into mepc, writes the cause code into mcause, clears the interrupt-enable bit in mstatus to prevent re-entry, and redirects the PC to the trap vector stored in mtvec. The mret instruction reverses this state to return to the interrupted code."
