# Modeling an Interrupt Controller and Vectoring

An interrupt controller is the traffic-cop between peripheral hardware and the CPU. It arbitrates simultaneous interrupt requests, assigns priorities, and tells the CPU exactly which handler to jump to. In a virtual prototype, modeling the interrupt controller correctly is the difference between a kernel that boots and one that hangs waiting for a timer tick.

## What an Interrupt Controller Does

1. **Collects** interrupt request lines (IRQ lines) from peripherals (UART, timer, DMA, GPIO).
2. **Masks** — enables or disables each source independently via mask registers.
3. **Prioritizes** — when multiple IRQs are pending, forwards the highest-priority one.
4. **Signals** the CPU via a dedicated interrupt wire.
5. **Vectors** — provides the CPU with an identifier so it can look up the correct Interrupt Service Routine (ISR) in the vector table.
6. **Acknowledges** — the software must write back to the interrupt controller after handling the interrupt so the controller can forward the next one.

## PLIC: RISC-V Platform-Level Interrupt Controller

The RISC-V PLIC (Platform-Level Interrupt Controller) is the standard external interrupt controller used with Linux/RISC-V. Its key MMIO registers:

| Register | Offset | Purpose |
|---|---|---|
| Priority | 0x000004 * N | Per-source priority (0 = disabled) |
| Pending  | 0x001000 + … | Bitmask: which IRQs are pending |
| Enable   | 0x002000 + … | Per-context enable bitmask |
| Threshold | 0x200000 + … | Per-context priority threshold |
| Claim/Complete | 0x200004 + … | Claim: read highest pending; Complete: write to EOI |

The Linux PLIC driver workflow:
```
1. Set source priority[N] > 0          (enable source)
2. Set context enable bit N            (enable for this hart/context)
3. Set context threshold = 0           (forward all priorities)
4. Interrupt fires → read Claim → get IRQ id
5. Dispatch to handler
6. Write IRQ id back to Claim/Complete (EOI)
```

> **Interview answer:** An interrupt controller collects, prioritizes, and masks IRQ lines; it signals the CPU and provides the interrupt ID so the OS can vector to the correct ISR; software must acknowledge (EOI) before the next interrupt of the same or lower priority is forwarded.

## Interrupt Vectoring

When the CPU takes an interrupt, it must jump to the correct handler. Two common schemes:

**Fixed vector (MIPS, older ARM)**
```
All exceptions → 0xBFC00380
Handler reads "cause" register to distinguish IRQ from trap
```

**Vectored interrupt (ARM GICv3, RISC-V with CLIC)**
```
Each IRQ → its own entry in a vector table
CPU indexes the table directly by interrupt ID
Eliminates the first-level dispatch overhead
```

On RISC-V with the standard PLIC (non-vectored mode), the trap handler reads `mcause`, checks the MSB (interrupt bit), reads the PLIC claim register to get the source ID, then calls the registered handler:

```c
void trap_handler(void) {
    uintptr_t cause = csr_read(mcause);
    if (cause >> (sizeof(uintptr_t)*8 - 1)) {   // interrupt bit set
        uint32_t irq = plic_claim();              // read claim register
        if (irq_handlers[irq]) irq_handlers[irq]();
        plic_complete(irq);                       // write EOI
    } else {
        handle_exception(cause);
    }
}
```

## Modeling the Interrupt Controller in a Virtual Prototype

```cpp
class PLICModel {
    uint32_t priority_[128] = {};
    uint32_t enable_[4]     = {};    // bitmask for 128 sources
    uint32_t pending_[4]    = {};
    uint32_t threshold_     = 0;
public:
    void raise_irq(int src) {
        pending_[src/32] |= (1u << (src%32));
        update_cpu_interrupt();
    }
    uint32_t claim() {
        // find highest-priority pending+enabled source above threshold
        int best = 0; uint32_t best_prio = 0;
        for (int i = 1; i < 128; i++) {
            if (is_pending(i) && is_enabled(i) && priority_[i] > threshold_) {
                if (priority_[i] > best_prio) { best = i; best_prio = priority_[i]; }
            }
        }
        if (best) pending_[best/32] &= ~(1u << (best%32));
        return best;
    }
    void complete(uint32_t src) { update_cpu_interrupt(); }
};
```

## Common Pitfalls

- **Forgetting EOI** — if the model does not clear the pending bit on claim and the driver does not write complete, the same interrupt fires forever.
- **Priority 0 = disabled** — a source at priority 0 must never be forwarded, even if its pending bit is set.
- **Threshold** — sources at or below the threshold must be suppressed. Many virtual prototype models skip this and fail on OS configurations that use threshold-based interrupt grouping.
- **Edge vs. level triggering** — edge-triggered: the pending bit is set on the rising edge and cleared by claim. Level-triggered: the peripheral must de-assert its IRQ line after acknowledge, or the pending bit is re-set immediately.

Accurate interrupt controller modeling is the single most common cause of OS boot failures on virtual prototypes.
