# Interrupt Priorities and Masking

Real systems have many interrupt sources. Without a priority scheme, a low-urgency event (e.g., a logging timer) could delay a high-urgency event (e.g., a motor fault signal). **Priority** determines which interrupt gets serviced first when multiple requests are pending simultaneously. **Masking** lets software suppress specific interrupts temporarily without losing them.

---

## Priority levels

Each interrupt source is assigned a numerical priority. Common conventions:

- **Higher number = higher priority** (ARM NVIC, RISC-V PLIC default).
- **Lower number = higher priority** (some legacy architectures).
- Priority 0 usually means "disabled" in RISC-V PLIC.

When two interrupts are pending simultaneously, the controller presents the higher-priority source to the CPU first.

```
Source A (priority 3) ─┐
Source B (priority 7) ─┤→ PLIC → CPU sees B first
Source C (priority 2) ─┘
```

---

## RISC-V PLIC priority and threshold

The PLIC exposes two controls:

| Register | Per-source or global | Effect |
|----------|----------------------|--------|
| `priority[n]` | Per source | 0 = disabled; 1–7 = priority level |
| `threshold`   | Per hart (CPU core) | Source is delivered only if `priority[n] > threshold` |

```c
// Enable source 5 at priority 3, threshold=1 on hart 0
PLIC->priority[5] = 3;
PLIC->enable[0][0] |= (1u << 5);   // enable bit for source 5
PLIC->threshold[0]  = 1;           // deliver if priority > 1
```

Raising the threshold temporarily masks lower-priority sources without touching their enable bits — a fast, atomic masking operation.

---

## Masking in RISC-V CSRs

RISC-V provides two levels of interrupt masking directly in CSRs:

### 1. Global interrupt enable

`mstatus.MIE` (Machine Interrupt Enable) is the master gate for all machine-mode interrupts.

```asm
csrci  mstatus, 8    # clear MIE bit (bit 3) — disable all M-mode interrupts
# ... critical section ...
csrsi  mstatus, 8    # set MIE bit — re-enable
```

### 2. Per-source enable

`mie` (Machine Interrupt Enable register) has individual bits for each interrupt type:

| Bit | Name | Interrupt |
|-----|------|-----------|
| 3   | MSIE | Machine software interrupt |
| 7   | MTIE | Machine timer interrupt |
| 11  | MEIE | Machine external interrupt |

```asm
li    t0, (1 << 7)   # MTIE bit
csrs  mie, t0        # set: enable timer interrupts
csrc  mie, t0        # clear: disable timer interrupts
```

---

## Priority inversion problem

A well-known pitfall: a high-priority task is blocked waiting for a resource held by a low-priority task, while a medium-priority task preempts the low-priority task. The high-priority task starves.

Solutions include **priority inheritance** (the low-priority task temporarily inherits the high-priority task's level) and **priority ceiling** protocols. These are primarily OS/RTOS concerns but stem from the hardware priority mechanism.

---

## Worked example: critical section with masking

```c
#include <stdint.h>

static inline void disable_irq(void) {
    __asm__ volatile ("csrci mstatus, 8" ::: "memory");
}

static inline void enable_irq(void) {
    __asm__ volatile ("csrsi mstatus, 8" ::: "memory");
}

void update_shared_buffer(const char *data, int len) {
    disable_irq();          // mask all M-mode interrupts
    // ... modify shared data structure ...
    enable_irq();           // restore
}
```

The `"memory"` clobber forces the compiler to complete all memory accesses before and after the barrier, preventing reordering across the mask boundary.

---

## Non-maskable interrupts (NMI)

Some interrupt sources bypass all masking — power failure, watchdog timeout, or hardware parity error. These **non-maskable interrupts (NMIs)** cannot be suppressed and always take priority. RISC-V implementations may define an NMI that jumps to a fixed reset-vector-like address. Software inside an NMI handler must assume the system may be in a corrupt state.

---

## Common pitfalls

- Forgetting to re-enable interrupts after a critical section (deadlock).
- Setting threshold too high — starves lower-priority peripherals.
- Failing to acknowledge (complete) an interrupt in the PLIC before returning — the same interrupt fires again immediately.
- Using global enable/disable for per-source control — coarser than necessary, introduces latency.

---

> **Interview answer:** Interrupt priority determines which of several simultaneously pending interrupts is serviced first. Masking suppresses delivery of an interrupt without losing the pending request — RISC-V provides global masking via `mstatus.MIE`, per-type masking via the `mie` CSR, and threshold-based masking in the PLIC so that sources below a priority level are silenced without clearing their enable bits.
