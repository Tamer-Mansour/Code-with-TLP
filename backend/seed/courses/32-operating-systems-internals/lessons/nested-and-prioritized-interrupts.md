# Nested Interrupts and Interrupt Priorities

Real systems receive multiple interrupts concurrently or in rapid succession. **Nested interrupts** allow a higher-priority ISR to preempt a lower-priority one that is already running. **Interrupt priorities** determine which source wins when multiple IRQs are pending simultaneously.

---

## Why Allow Nesting?

Without nesting, a low-priority ISR (e.g., a slow disk controller) can delay a high-priority ISR (e.g., a real-time audio timer) for the entire duration of the low-priority handler. With nesting, the high-priority ISR preempts the low-priority one and runs immediately.

```
Time ──────────────────────────────────────────────────►
Low-priority ISR:   [== running ========] resumes ══════►
High-priority ISR:               [== runs ==]
                                ▲ nested entry
```

---

## How the CPU Enables Nesting

When an **interrupt gate** is entered, the CPU automatically clears `IF` (disables interrupts). For nesting to occur, the ISR must explicitly **re-enable interrupts** after saving state and acknowledging the controller:

```asm
; Inside an ISR — allow higher-priority IRQs to nest
push_all_regs
send_EOI_to_APIC
sti              ; re-enable interrupts — NOW higher-priority IRQs can preempt
; ... body of ISR ...
cli              ; disable before restoring state (avoid partial-state interrupt)
pop_all_regs
iret
```

The key sequence is: **save state → EOI → sti → work → cli → restore → iret**.

---

## Interrupt Priority Levels

### Legacy 8259A PIC

The classic PC had two cascaded 8259A chips providing 15 IRQ lines (IRQ0–IRQ15). Priority was **fixed**: IRQ0 (timer) had the highest priority, IRQ7 the lowest among the primary chip.

```
IRQ 0  — Timer (highest priority)
IRQ 1  — Keyboard
IRQ 2  — Cascade to secondary PIC
IRQ 3  — COM2
IRQ 4  — COM1
IRQ 5  — LPT2 / Sound Card
IRQ 6  — Floppy
IRQ 7  — LPT1 (lowest on primary)
IRQ 8  — RTC
...
IRQ 15 — Secondary IDE (lowest on secondary)
```

### APIC Priority

The APIC uses **interrupt priority levels (IPL)** encoded in the **Task Priority Register (TPR)**. Only interrupts with a vector higher than `TPR × 16` are delivered. This allows the OS to mask entire ranges of lower-priority interrupts by raising TPR.

```c
// Raise CPU priority to mask all vectors below 0xF0
*((volatile uint32_t *)LAPIC_TPR) = 0xF0;
// ... critical section ...
*((volatile uint32_t *)LAPIC_TPR) = 0x00; // lower priority
```

---

## Linux Interrupt Priority Model

Linux does not use hardware priority registers directly. Instead it uses a software model:

| Level | Preemptable by | Examples |
|-------|---------------|---------|
| User process | All of the below | `ls`, `nginx` |
| Softirq/Tasklet | Hardware IRQ | NET_RX, BLOCK |
| Hardware ISR (top half) | NMI only | NIC ISR, timer ISR |
| NMI handler | Nothing | Watchdog, hardware error |

By default, Linux disables interrupts for the duration of each ISR (no nesting), choosing safety over low latency. PREEMPT_RT patches change this to allow threaded IRQs.

---

## Threaded IRQs (Linux PREEMPT_RT)

In the PREEMPT_RT patchset, most ISRs are converted into **kernel threads**:

```c
// Register a threaded IRQ handler
request_threaded_irq(
    irq,
    primary_handler,    // runs in interrupt context (minimal)
    thread_fn,          // runs in a kernel thread (can sleep, be scheduled)
    IRQF_ONESHOT,
    "my_driver",
    dev
);
```

The kernel thread has a real-time scheduling priority (SCHED_FIFO), so priority is managed by the scheduler rather than the hardware IRQ level.

---

## Double Fault and Interrupt Stack Table

If an ISR itself triggers a fault (e.g., stack overflow causing a page fault in the ISR), the CPU may not have a valid stack for the nested exception. The **IST (Interrupt Stack Table)** mechanism allows the CPU to switch to a pre-allocated, always-valid emergency stack:

```c
// IDT entry: IST field = 1 → use IST[1] (double-fault stack)
idt[8].ist = 1;   // #DF (double fault)
```

---

## Common Pitfalls

- **Forgetting EOI before sti** — if sti precedes EOI, the same IRQ can re-enter immediately, creating an infinite loop.
- **Stack overflow from deep nesting** — each nested ISR uses stack space. Bound the nesting depth.
- **Priority inversion** — a high-priority ISR waiting on a lock held by a low-priority ISR starves.

> **Interview answer:** Nested interrupts let a higher-priority ISR preempt a lower-priority one by re-enabling IF after EOI. Priority is determined by the APIC vector level or the OS scheduling priority (for threaded IRQs). The CPU itself disables interrupts on ISR entry via an interrupt gate; nesting is opt-in, requiring explicit `sti` in the ISR body.
