# Maskable vs Non-Maskable Interrupts

Not all interrupts can be silenced. The distinction between **maskable** and **non-maskable** interrupts (NMIs) determines which hardware events the OS can defer and which demand immediate unconditional attention.

---

## Maskable Interrupts (MI)

A maskable interrupt is one that the CPU will **ignore when the IF (Interrupt Flag) is clear** (i.e., after a `cli` instruction).

- Controlled by the `IF` bit in `RFLAGS`.
- Set with `sti` (set IF), cleared with `cli` (clear IF).
- Entering an interrupt gate automatically clears IF.
- Most hardware IRQs (timer, keyboard, disk, NIC) are maskable.

```asm
cli         ; disable all maskable interrupts
; ... critical section: touching shared data structures ...
sti         ; re-enable maskable interrupts
```

The OS uses masking to create **atomic critical sections** without needing hardware compare-and-swap. The downside is that latency for all maskable IRQs increases while interrupts are disabled.

---

## The APIC IMR (Interrupt Mask Register)

Beyond the global IF flag, individual IRQ lines can be masked at the **APIC level** using the Interrupt Mask Register. This lets the OS selectively disable specific devices without affecting others.

```c
// Mask IRQ line 5 in the APIC I/O redirect table
uint32_t entry = ioapic_read(IOAPIC_REDTBL + 5*2);
entry |= (1 << 16);   // set mask bit
ioapic_write(IOAPIC_REDTBL + 5*2, entry);
```

This is how `disable_irq(5)` works in the Linux kernel.

---

## Non-Maskable Interrupts (NMI)

An NMI is an interrupt that **cannot be masked by the IF flag** and cannot be disabled through normal software means. It demands immediate CPU attention regardless of the current execution state.

On x86, the NMI is delivered via a dedicated CPU pin (or APIC NMI route) and always uses **vector 2**.

### When Are NMIs Used?

| Use Case | Why NMI? |
|----------|----------|
| Hardware memory error (ECC) | Must report before data corruption propagates |
| Watchdog timer | Must fire even if the kernel is stuck in a spinloop with IF=0 |
| Performance monitoring (PMU overflow) | Must capture counter overflow accurately |
- NMI shootdown (profilers like `perf`) | Must stop remote CPUs regardless of their state |
| IOCK# (I/O check) bus error | Fatal hardware failure |

---

## NMI Handler Constraints

The NMI handler is the most constrained code in the kernel because:

1. It can interrupt **any code**, including another NMI handler (NMIs can partially nest on x86).
2. It runs with **both maskable interrupts and NMI delivery disabled** on the current CPU.
3. It must use its own dedicated stack (via IST in the IDT) to avoid stack corruption.
4. It cannot use `iret` directly in all cases on x86-64 because `iret` re-enables NMIs — the kernel uses a careful `iretq` trampoline.

```c
// Linux NMI handler signature
void do_nmi(struct pt_regs *regs, long error_code) {
    // Check NMI source (hardware error? watchdog? perf PMU?)
    if (nmi_handle(NMI_LOCAL, regs)) {
        // handled
    } else {
        // unknown NMI — log and optionally panic
        pr_warn("Unknown NMI\n");
    }
}
```

---

## Pseudo-NMI (pNMI) on ARM

ARM processors do not have a hardware NMI pin in the classic sense. Recent ARM cores support **priority masking** via `PMR` (Priority Mask Register) to simulate NMI behavior: a "superpriority" interrupt that fires even when `DAIF.I` (the normal mask bit) is set.

```
DAIF register bits:
  D — Debug
  A — SError
  I — IRQ (maskable)
  F — FIQ (fast interrupt, historically higher priority)
```

On ARMv8.1-M and newer, a dedicated NMI feature is part of the architecture.

---

## Comparison Table

| Property | Maskable Interrupt | NMI |
|----------|--------------------|-----|
| Disabled by `cli` / `DAIF.I=1` | Yes | No |
| Can be masked per-device at APIC | Yes | No (special NMI-specific masking) |
| Vector (x86) | 32–255 | 2 |
| Typical sources | Timer, NIC, disk, keyboard | ECC error, watchdog, PMU |
| ISR can sleep? | No | Absolutely not |
| Can nest? | Yes (with `sti`) | Partially (x86 NMI-within-NMI has special handling) |

---

## Worked Example

A system watchdog fires every 10 ms. If the kernel detects no heartbeat for 30 ms, it triggers a panic. The watchdog uses an NMI so it fires even if:

- A spinlock holder has called `cli`.
- A buggy driver is stuck in an infinite loop in ISR context.
- A deadlock has frozen all kernel threads.

Without the NMI, a kernel hang would be truly undetectable in hardware.

> **Interview answer:** Maskable interrupts can be deferred by clearing the IF flag (`cli` on x86); the OS uses this to protect critical sections. Non-maskable interrupts bypass the IF flag entirely and are used for unignorable events like hardware memory errors, watchdogs, and performance counters. On x86, NMIs always use vector 2 and have special constraints around nesting and stack usage.
