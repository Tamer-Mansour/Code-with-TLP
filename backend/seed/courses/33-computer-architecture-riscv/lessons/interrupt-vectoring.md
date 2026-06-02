# Interrupt Vectoring and Vector Tables

When a trap fires, the processor must jump to the correct handler. **Interrupt vectoring** is the mechanism by which the hardware determines the target address. There are two broad strategies: a single entry point (direct mode) and a table of per-cause entry points (vectored mode). Understanding both is critical for embedded systems programming and OS kernel development.

---

## Direct Mode (Non-Vectored)

In direct mode the processor always jumps to the same base address regardless of the cause. The handler code is responsible for reading `mcause` and dispatching to the appropriate sub-handler.

```
mtvec = BASE | 0      (mode bits = 00)
Trap fires → PC = BASE
```

```asm
trap_entry:
    csrr   t0, mcause
    li     t1, 0x80000007   # machine timer interrupt
    beq    t0, t1, handle_timer
    li     t1, 8            # ecall from U-mode
    beq    t0, t1, handle_syscall
    j      handle_other
```

Advantage: simple, single handler, easy to debug.  
Disadvantage: software dispatch adds latency.

---

## Vectored Mode

In vectored mode the processor computes the handler address directly from the cause code, skipping software dispatch.

```
mtvec = BASE | 1      (mode bits = 01)

For exceptions:  PC = BASE          (all exceptions still go to BASE)
For interrupts:  PC = BASE + 4 * cause_code
```

The vector table is an array of 4-byte entries at `BASE`, each containing a jump instruction:

```asm
.align 4
vector_table:
    j    handle_default         # cause 0
    j    handle_supervisor_sw   # cause 1
    j    handle_default         # cause 2 (reserved)
    j    handle_machine_sw      # cause 3
    j    handle_default         # cause 4 (reserved)
    j    handle_supervisor_timer # cause 5
    j    handle_default         # cause 6
    j    handle_machine_timer   # cause 7
    j    handle_default         # cause 8 (reserved)
    j    handle_supervisor_ext  # cause 9
    j    handle_default         # cause 10 (reserved)
    j    handle_machine_ext     # cause 11
```

Setting the vector base in RISC-V:

```asm
la    t0, vector_table
ori   t0, t0, 1          # set mode = vectored
csrw  mtvec, t0
```

---

## Alignment requirements

`mtvec` requires the BASE address to be aligned to at least 4 bytes. For vectored mode, many implementations require 64-byte or even 256-byte alignment to ensure that the table entries do not cross cache lines in ways that introduce extra latency. Always check the specific implementation's documentation.

---

## External interrupt controllers

For systems with many peripheral interrupt sources, a dedicated **interrupt controller** aggregates lines before presenting them to the CPU. RISC-V uses the **Platform-Level Interrupt Controller (PLIC)**:

```
Peripheral IRQs → PLIC → single "external interrupt" line → CPU
```

The PLIC assigns each source a priority and an ID. When the CPU takes the machine-external interrupt (`mcause = 0x8000000B`), it reads the PLIC's **claim register** to discover which source ID fired, then reads its own lookup table to call the right sub-handler:

```c
void handle_machine_ext(void) {
    uint32_t source = PLIC->claim;   // read and claim the interrupt
    irq_handlers[source]();          // software table dispatch
    PLIC->complete = source;         // signal completion
}
```

This is a **two-level vectoring** scheme: hardware vectoring to the external-interrupt handler, then software vectoring within the PLIC driver.

---

## Comparison table

| Property            | Direct mode                  | Vectored mode                     |
|---------------------|------------------------------|-----------------------------------|
| Dispatch overhead   | Software (branch chain)      | Hardware (address calculation)    |
| Code complexity     | Simple single entry point    | Requires aligned jump table       |
| Interrupt latency   | Higher                       | Lower                             |
| Exception handling  | Same as interrupts           | Still goes to BASE                |
| Use case            | Prototyping, RTOS w/ few IRQs | Production firmware, real-time    |

---

## Worked example: setting up vectored mode in bare-metal C

```c
extern void __trap_vector[];    // defined in linker script / asm

void setup_vectored_traps(void) {
    uintptr_t vec = (uintptr_t)__trap_vector;
    vec |= 1;                   // vectored mode bit
    asm volatile("csrw mtvec, %0" :: "r"(vec));
}
```

The linker script places `__trap_vector` at a 256-byte aligned address, and the assembly file defines one `j handler_N` per interrupt cause.

---

> **Interview answer:** Interrupt vectoring is the hardware mechanism that maps a cause code to a handler address. Direct mode always jumps to a single entry point and uses software dispatch; vectored mode computes `BASE + 4 * cause` to jump directly to the right handler, reducing latency. RISC-V selects the mode via the two low bits of `mtvec`.
