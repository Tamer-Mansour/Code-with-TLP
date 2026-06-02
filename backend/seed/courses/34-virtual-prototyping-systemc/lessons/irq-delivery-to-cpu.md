# Delivering an IRQ to the CPU Model

Getting an interrupt signal from the interrupt controller to the CPU model is conceptually simple — but the CPU model must implement the correct architectural interrupt entry sequence so that software running inside the VP behaves exactly as it would on real hardware.

## The CPU's View of an IRQ

When the CPU's interrupt input line is asserted and interrupts are globally enabled (e.g., MIE bit set in RISC-V `mstatus`, or I-bit cleared in ARM CPSR), the CPU must:

1. **Finish the current instruction** (or abort it for precise exceptions).
2. **Save the program counter** to a link/exception register (e.g., `mepc` on RISC-V, `LR` on ARM).
3. **Save the processor status** (e.g., push CPSR, save `mstatus`).
4. **Set the cause register** to identify which interrupt fired.
5. **Jump to the vector table** entry for interrupts.

In a VP, all five steps are implemented inside the CPU model's instruction loop.

## SystemC Integration Pattern

The most common pattern is a **polling check at instruction decode**:

```cpp
// Inside the CPU's instruction execution loop
void CPU::execute_one_instruction() {
    // Check for pending interrupt before fetching next instruction
    if (irq_in.read() && interrupts_enabled()) {
        enter_interrupt_handler();
        return;
    }
    uint32_t instr = fetch();
    decode_and_execute(instr);
}
```

The `irq_in` signal is an `sc_in<bool>` connected to the PLIC/GIC output. Because `sc_in::read()` is non-blocking, the CPU checks it at every instruction boundary without adding simulation overhead.

## Alternative: Event-Driven Wake-Up

For instruction-set simulators that use `wait()` internally (ISS implemented as an `SC_THREAD`), you can wake up immediately on IRQ assertion:

```cpp
void CPU::run() {
    while (true) {
        if (irq_in.read() && interrupts_enabled()) {
            enter_interrupt_handler();
        } else {
            execute_one_instruction();
        }
        // Advance simulation time by one cycle
        wait(cycle_period, SC_NS);
    }
}

// Alternatively, combine time advance with event sensitivity:
void CPU::run() {
    sc_event irq_event;
    while (true) {
        wait(cycle_period, SC_NS, irq_event);  // wake early on IRQ
        if (irq_in.read() && interrupts_enabled()) {
            enter_interrupt_handler();
        } else {
            execute_one_instruction();
        }
    }
}
```

## Implementing enter_interrupt_handler()

For a RISC-V M-mode model:

```cpp
void CPU::enter_interrupt_handler() {
    // 1. Save PC
    csr_mepc = pc;
    // 2. Save and update mstatus (disable further interrupts)
    csr_mstatus = (csr_mstatus & ~MSTATUS_MIE) |
                  ((csr_mstatus & MSTATUS_MIE) ? MSTATUS_MPIE : 0);
    // 3. Set cause (MSB=1 for interrupt, lower bits = IRQ number)
    csr_mcause = (1u << 31) | irq_number_from_plic();
    // 4. Jump to interrupt vector
    pc = csr_mtvec & ~3u;   // direct mode: base address
}
```

## Interrupt Return (MRET / ERET)

The ISR ends with a return instruction that reverses the entry sequence:

```cpp
void CPU::execute_mret() {
    pc          = csr_mepc;
    csr_mstatus = restore_mie_from_mpie(csr_mstatus);
}
```

This is what allows nested interrupts to work correctly — each entry saves and each return restores the interrupt-enable state.

## Timing Considerations

| Aspect | Consideration |
|---|---|
| Interrupt latency | Model should add a small delay (pipeline flush) to be realistic |
| WFI (Wait For Interrupt) | CPU should `wait(irq_event)` instead of spinning — crucial for fast simulation |
| IRQ de-assertion timing | CPU should not re-enter ISR in the same delta cycle after return |

## Common Pitfalls

- **No WFI optimization:** Without a proper WFI (`wait()` on the IRQ event), the simulator burns 100 % of host CPU executing NOP-equivalent cycles.
- **Skipping MPIE/SPIE:** Failing to save the previous interrupt-enable bit breaks nested interrupt restore.
- **Checking IRQ after every micro-op:** In a pipelined model, check at instruction retire boundaries, not at every pipeline stage.

> **Interview answer:** The CPU model checks the IRQ input signal at each instruction boundary; when asserted and interrupts are enabled, it saves the PC and processor status to exception registers, sets the cause register, and jumps to the vector table — exactly mirroring the hardware interrupt entry sequence.
