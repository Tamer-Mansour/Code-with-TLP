# Quiz: Interrupts, Exceptions, and Traps

Test your understanding of the key concepts from this module.

---

**Q1. A process executes a `div` instruction with a zero divisor. What type of event does the CPU generate?**

- [ ] Maskable hardware interrupt
- [x] Synchronous exception (fault)
- [ ] Non-maskable interrupt
- [ ] Software trap triggered by the OS

A divide-by-zero is caused directly by the currently-executing instruction, making it a synchronous CPU exception (specifically a fault on x86, vector 0 #DE).

---

**Q2. Which of the following correctly describes the x86 real-mode IVT entry for vector N?**

- [ ] A 16-byte descriptor containing a 64-bit handler address, DPL, and IST index
- [ ] A 2-byte offset into the kernel code segment
- [x] A 4-byte little-endian pair of (16-bit offset, 16-bit segment) at address N×4
- [ ] An 8-byte entry containing a 32-bit linear address and a 32-bit attribute word

In real mode, the IVT lives at 0x00000 and each entry is exactly 4 bytes: a 16-bit offset followed by a 16-bit segment, both little-endian. The linear address is `segment × 16 + offset`.

---

**Q3. An Interrupt Service Routine (ISR) is executing. Which of the following actions is FORBIDDEN inside an ISR?**

- [ ] Reading from a memory-mapped I/O register
- [ ] Incrementing a global atomic counter
- [ ] Sending an EOI to the APIC
- [x] Calling `sleep()` or blocking on a mutex

ISRs run in interrupt context where sleeping is not permitted — there is no process context to schedule back to. Blocking would deadlock the kernel. Reading MMIO, using atomics, and sending EOI are all valid ISR operations.

---

**Q4. What is the purpose of the `iret` (or `iretq`) instruction at the end of an ISR?**

- [ ] To send an End-Of-Interrupt signal to the APIC
- [ ] To switch from ring 0 to ring 3 using the GDT
- [x] To atomically restore RFLAGS, CS, and RIP (and optionally RSP/SS) saved by the CPU on interrupt entry
- [ ] To flush the TLB and reload CR3

`iret` pops the CPU state that the hardware pushed automatically when the interrupt fired — RFLAGS, CS, and EIP/RIP — and if there was a privilege level change, also RSP and SS. This restores the interrupted code's execution context atomically.

---

**Q5. A system must guarantee that a real-time audio ISR fires within 50 µs of the hardware timer tick. Which factor is MOST likely to cause this deadline to be missed?**

- [ ] The ISR sending an EOI to the APIC
- [ ] The CPU performing a TLB shootdown IPI
- [x] A long `cli`-protected critical section in an unrelated kernel driver
- [ ] The `iret` instruction taking more than one cycle

While EOI, TLB shootdowns, and `iret` all take time, a long window with `IF=0` (interrupts disabled) is the most common cause of excessive interrupt latency on general-purpose systems, as it prevents the CPU from delivering the IRQ even after the hardware asserts it.

---

**Q6. Which statement about Non-Maskable Interrupts (NMIs) is TRUE?**

- [ ] NMIs are masked when the CPU executes the `cli` instruction
- [ ] NMIs use a dynamically assigned vector chosen by the OS at boot
- [ ] NMIs can be individually disabled per-device in the APIC I/O redirection table
- [x] NMIs bypass the IF flag and always use vector 2 on x86, making them suitable for hardware watchdogs

NMIs are not controlled by the IF flag (`cli`/`sti` have no effect on them). On x86, the NMI is always delivered on vector 2. This makes them ideal for watchdog timers and hardware error reporting because they fire even when the kernel has disabled all maskable interrupts.
