# Modeling an Interrupt Controller (PLIC/GIC)

Real SoCs never connect peripheral IRQ lines directly to the CPU. An **Interrupt Controller** sits between them, providing prioritization, masking, and routing. In RISC-V systems this is the PLIC (Platform-Level Interrupt Controller); in ARM systems it is the GIC (Generic Interrupt Controller). Modeling one correctly in a VP ensures that any software using the interrupt controller's MMIO registers works without modification.

## Responsibilities of an Interrupt Controller

- **Aggregation:** Accept IRQ signals from many peripherals (the PLIC supports up to 1023 sources).
- **Priority:** Each source has a configurable priority. Only sources whose priority exceeds the current threshold generate a CPU interrupt.
- **Masking / Enable:** Software can enable or disable individual sources per hart/CPU context.
- **Claim / Complete:** The CPU reads a CLAIM register to acknowledge the highest-priority pending interrupt; it writes COMPLETE when the ISR finishes.

## PLIC Register Map (Simplified)

| Offset | Register | Purpose |
|---|---|---|
| 0x000004 | PRIORITY[1] | Priority of source 1 (0–7) |
| 0x001000 | PENDING[0] | Bitmask of pending sources 0–31 |
| 0x002000 | ENABLE[0] | Enable bitmask for hart 0 |
| 0x200000 | THRESHOLD | Minimum priority to forward to CPU |
| 0x200004 | CLAIM/COMPLETE | Read=claim, Write=complete |

## SystemC Structure

```cpp
SC_MODULE(PLIC) {
    // IRQ inputs from peripherals (up to N sources)
    sc_vector<sc_in<bool>> irq_src;

    // IRQ output to CPU
    sc_out<bool> irq_to_cpu;

    // TLM target socket for MMIO register access
    tlm_utils::simple_target_socket<PLIC> socket;

    uint32_t priority[1024];  // per-source priority
    uint32_t pending[32];     // pending bitmask (1024 sources / 32)
    uint32_t enable[32];      // enable bitmask per hart
    uint32_t threshold;       // hart priority threshold
    uint32_t claimed_id;      // currently claimed source ID

    void irq_update();        // sc_method — recomputes irq_to_cpu
    void b_transport(tlm::tlm_generic_payload&, sc_time&);

    SC_CTOR(PLIC) : irq_src("irq_src", 32), socket("socket") {
        SC_METHOD(irq_update);
        for (auto& sig : irq_src) sensitive << sig;
        socket.register_b_transport(this, &PLIC::b_transport);
    }
};
```

## The irq_update Logic

```cpp
void PLIC::irq_update() {
    // Update pending bits from input signals
    for (int i = 1; i < 32; i++) {
        if (irq_src[i].read()) {
            pending[i / 32] |= (1u << (i % 32));
        }
    }
    // Find highest-priority enabled pending source
    int best_id  = 0;
    int best_pri = 0;
    for (int i = 1; i < 32; i++) {
        bool pend = (pending[i/32] >> (i%32)) & 1;
        bool enab = (enable[i/32]  >> (i%32)) & 1;
        if (pend && enab && (int)priority[i] > best_pri) {
            best_pri = priority[i];
            best_id  = i;
        }
    }
    // Assert to CPU only if best priority > threshold
    irq_to_cpu.write(best_id != 0 && best_pri > (int)threshold);
}
```

## Claim and Complete Flow

When the CPU reads the CLAIM register:
1. The PLIC returns the ID of the highest-priority pending interrupt.
2. The PLIC clears that source's pending bit — preventing re-assertion.
3. The PLIC recomputes `irq_to_cpu`.

When the CPU writes the COMPLETE register with the same ID:
1. The PLIC marks that source as no longer in-service.
2. If the peripheral line is still high (level-triggered), the pending bit may be set again.

## GIC vs PLIC: Key Differences

| Feature | PLIC (RISC-V) | GIC (ARM) |
|---|---|---|
| Interrupt ID width | 10-bit (1023 sources) | 10-bit (1020 sources) |
| Priority levels | Implementation-defined | 8–256 levels |
| Acknowledgment | CLAIM/COMPLETE registers | IAR/EOIR registers |
| SPI / SGI | Not named | SGI (software), SPI (shared) |
| Security extensions | No | GICv3+ with security states |

## Common Pitfalls

- **Missing pending-clear on claim:** If you forget to clear the pending bit in `b_transport` CLAIM, software falls into an infinite ISR loop.
- **Priority=0 means disabled:** In the PLIC spec, priority 0 effectively disables a source regardless of the enable bit.
- **Threshold register per context:** Each CPU hart has its own threshold — a mistake is using a global threshold for all harts.

> **Interview answer:** An interrupt controller model (PLIC/GIC) in a VP is a TLM target with MMIO registers that software configures, plus an `sc_method` sensitive to all peripheral IRQ signals that recomputes a single aggregated interrupt line to the CPU based on priority, masking, and threshold.
