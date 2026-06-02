# Interrupt Priorities and Nesting

Real systems handle dozens of simultaneous interrupt sources. Not all events are equally urgent — a real-time motor control interrupt must preempt a background UART receive interrupt. **Interrupt priorities** enforce this ordering, and **interrupt nesting** allows a higher-priority interrupt to preempt an already-running ISR.

## Priority Basics

Every interrupt source is assigned a numeric priority level. Convention varies by architecture:

| Architecture | Priority Range | Higher Priority = |
|---|---|---|
| RISC-V PLIC | 0–7 (or deeper) | Higher number |
| ARM GIC | 0–255 | Lower number |
| ARM Cortex-M NVIC | 0–255 | Lower number |
| x86 APIC | 0–15 (class) | Higher number |

The interrupt controller compares each pending source's priority against the **current priority threshold** (called Threshold in PLIC, PMR in Cortex-M, TPR in APIC). Only sources that **exceed** the threshold are forwarded to the CPU.

## Priority in the PLIC Model

```cpp
void PLIC::irq_update() {
    int best_id  = 0;
    int best_pri = 0;
    for (int i = 1; i < NUM_SOURCES; i++) {
        if (is_pending(i) && is_enabled(i) &&
            (int)priority[i] > (int)threshold &&   // exceeds threshold
            (int)priority[i] > best_pri) {          // higher than current best
            best_pri = priority[i];
            best_id  = i;
        }
    }
    irq_to_cpu.write(best_id != 0);
    claimed_candidate = best_id;
}
```

When the CPU claims the interrupt it learns `best_id`, which it uses to dispatch to the correct ISR.

## Interrupt Nesting

Nesting allows a higher-priority interrupt to preempt a lower-priority ISR that is currently executing:

1. ISR for source A (priority 3) is running.
2. Source B (priority 7) fires.
3. CPU: detects priority 7 > current threshold (3), saves state again, enters ISR-B.
4. ISR-B runs and completes, returns.
5. ISR-A resumes.

### Enabling Nesting in Hardware

On RISC-V (PLIC + CPU), nesting requires software to:
- **Re-enable global interrupts (MIE)** at the top of the ISR.
- **Raise the PLIC threshold** to the current IRQ's priority so lower-priority sources cannot preempt.
- **Save and restore `mepc`/`mcause`** on the stack (the hardware saves these, but the next interrupt will overwrite them — so the ISR must push them before re-enabling MIE).

```c
void isr_source_a(void) {
    // Save hardware exception registers
    uint32_t saved_mepc   = read_csr(mepc);
    uint32_t saved_mcause = read_csr(mcause);
    // Raise PLIC threshold to current priority (3)
    plic->threshold = 3;
    // Re-enable global interrupts — nesting enabled
    set_csr(mstatus, MSTATUS_MIE);

    do_work_for_source_a();

    // Restore
    clear_csr(mstatus, MSTATUS_MIE);
    plic->threshold = 0;
    write_csr(mepc,   saved_mepc);
    write_csr(mcause, saved_mcause);
}
```

## Modeling Nesting in the VP

The CPU model must track the **interrupt priority stack**:

```cpp
std::stack<int> priority_stack;   // tracks in-service IRQ priorities

void CPU::enter_interrupt_handler(int irq_priority) {
    priority_stack.push(irq_priority);
    // ... save context, jump to ISR ...
}

void CPU::handle_mret() {
    if (!priority_stack.empty()) priority_stack.pop();
    // ... restore context ...
}
```

The PLIC threshold register is updated by software — the VP model automatically adjusts which IRQs are forwarded based on the current threshold value.

## Priority Inversion

A classic hazard: a low-priority task holds a mutex, a high-priority ISR tries to acquire it, and the system deadlocks. The solution in real-time systems is **priority inheritance** — temporarily boost the low-priority holder's effective priority.

VPs typically do not model priority inheritance at the hardware level (it is a software protocol), but understanding the problem is critical for embedded systems interviews.

## Common Pitfalls

- **Priority = 0 treated as lowest:** In PLIC, priority 0 disables the source entirely. Do not use 0 as "lowest active priority".
- **Forgetting threshold on ISR entry:** Without raising the threshold, all same-or-lower-priority interrupts can nest infinitely.
- **Stack overflow from deep nesting:** Each nested interrupt consumes a stack frame. A VP can expose this by simulating a finite stack.

> **Interview answer:** Interrupt priorities prevent lower-urgency events from preempting critical ISRs. The interrupt controller compares each pending source's priority against a configurable threshold and forwards only those that exceed it. Nesting is enabled when the CPU re-enables global interrupts inside an ISR after raising the threshold to the current level.
