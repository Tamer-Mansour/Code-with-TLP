# Nested and Reentrant Interrupt Handling

By default, when RISC-V takes a machine-mode trap it clears `mstatus.MIE` to zero, preventing any further machine-mode interrupts while the handler runs. This is safe but adds latency: a low-priority, long-running handler can delay a high-priority, time-critical handler. **Nested interrupts** solve this by re-enabling interrupts inside a handler, allowing a higher-priority interrupt to preempt the current one.

---

## Default (non-nested) behavior

```
Timer IRQ fires:
  hardware clears MIE → enters handler
  UART IRQ fires:
    MIE=0, so UART IRQ is pending but not delivered
  handler returns, MIE restored (MPIE→MIE)
  NOW the UART IRQ is delivered (late!)
```

For hard real-time systems, this additional latency may violate timing constraints.

---

## Enabling nested interrupts

To allow preemption inside a handler, the handler must:

1. Save the full context (including `mepc`, `mstatus`, and all registers) — because the next trap will overwrite them.
2. Re-enable `mstatus.MIE`.
3. Disable the current interrupt source (or lower its priority) to prevent re-entrant invocation of itself.
4. Restore `mepc`, `mstatus`, and all registers on exit.

```asm
nested_trap_entry:
    addi  sp, sp,   -272
    # Save all 32 GPRs + mepc + mstatus
    sd    ra,    0(sp)
    # ... save t0-t6, a0-a7, s0-s11, gp, tp ...
    csrr  t0, mepc
    sd    t0,  256(sp)
    csrr  t0, mstatus
    sd    t0,  264(sp)

    # Re-enable interrupts — allow higher-priority preemption
    csrsi mstatus, 8     # set MIE

    call  c_trap_handler

    # Disable interrupts before restoring state
    csrci mstatus, 8     # clear MIE

    ld    t0,  264(sp)
    csrw  mstatus, t0
    ld    t0,  256(sp)
    csrw  mepc, t0
    ld    ra,    0(sp)
    # ... restore all registers ...
    addi  sp, sp,  272
    mret
```

---

## Reentrant handlers

A **reentrant handler** is one that can safely be called again (by a second instance of the same interrupt) before the first invocation finishes. Requirements:

- All state is on the stack (no static/global variables that would be corrupted).
- The interrupt source is acknowledged and re-armed before re-enabling `MIE`.
- Stack depth is bounded — the system must have enough stack for the maximum nesting depth.

```c
// Reentrant-safe: all state is local
void __attribute__((interrupt)) uart_irq_handler(void) {
    // acknowledge the UART interrupt first
    uint8_t ch = UART->data;          // reading clears the interrupt flag
    // re-enable global interrupts (higher-priority IRQs can now preempt)
    enable_irq();
    // process ch — purely local state
    ring_buffer_push(&rx_buf, ch);    // ring_buffer_push must also be reentrant!
    disable_irq();                    // guard before mret
}
```

---

## Stack depth analysis

Allowing N levels of nesting requires at minimum:

```
stack_needed = N × frame_size_per_handler + safety_margin
```

For a RISC-V RV64 system saving all 32 registers plus two CSRs:

```
frame_size = (32 + 2) × 8 = 272 bytes
4 levels   = 4 × 272 = 1088 bytes minimum interrupt stack
```

Undersizing the interrupt stack leads to silent memory corruption — one of the most difficult bugs to debug.

---

## Priority-based gating

Rather than enabling all interrupts unconditionally, well-designed systems raise the PLIC threshold to the current interrupt's priority before re-enabling `MIE`. This allows only strictly higher-priority sources to preempt:

```c
void handle_external_irq(void) {
    uint32_t src = PLIC->claim;
    uint32_t old_thresh = PLIC->threshold;
    PLIC->threshold = PLIC->priority[src];  // block same-or-lower priority
    enable_irq();                            // allow higher priority only

    irq_handlers[src]();

    disable_irq();
    PLIC->threshold = old_thresh;
    PLIC->complete  = src;
}
```

---

## Supervisor vs Machine mode nesting in RISC-V

RISC-V also supports S-mode (supervisor) interrupts preempting U-mode (user) code while M-mode is already handling an interrupt — a form of cross-privilege nesting managed by `mideleg` (interrupt delegation) and `sideleg` (sub-delegation) registers. The OS kernel typically handles interrupts at S-mode, while firmware handles them at M-mode.

---

## Common pitfalls

- Re-enabling `MIE` before saving `mepc`/`mstatus` — the next trap overwrites the saved PC.
- Forgetting to disable `MIE` after the C handler returns but before restoring CSRs.
- Shared non-reentrant data structures (e.g., `printf` with a global buffer) called from reentrant handlers.
- Infinite nesting of the same interrupt (must acknowledge/mask before re-enabling).

---

> **Interview answer:** Nested interrupts are enabled by re-enabling `mstatus.MIE` inside the trap handler after saving `mepc` and `mstatus` on the stack, so a higher-priority interrupt can preempt the running handler. The handler must save all architectural state, acknowledge or mask the current source, re-enable global interrupts, and restore everything before `mret`. The main risk is stack overflow from unbounded nesting depth.
