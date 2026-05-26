# Quiz: I/O and Performance

**Q1. Which I/O technique has the CPU spin in a tight loop checking a device status register?**
- [x] Polling (busy-wait)
- [ ] Interrupt-driven I/O
- [ ] DMA transfer
- [ ] Memory-mapped I/O

**Q2. With DMA (Direct Memory Access), CPU involvement is limited to:**
- [ ] Copying every byte between device registers and memory.
- [ ] Only the address translation phase.
- [x] Initiating the transfer (writing DMA parameters) and handling the completion interrupt.
- [ ] No involvement; DMA is fully autonomous and never interrupts the CPU.

**Q3. A program has 70% of its execution time in a parallelizable kernel. Using Amdahl's Law with infinite processors, the maximum overall speedup is:**
- [ ] 70×
- [ ] Infinite
- [x] 3.33×
- [ ] 1.43×

**Q4. A program runs in 10 seconds. You improve a section that takes 6 seconds of that to run 3× faster. The new execution time is:**
- [ ] 3.33 seconds
- [x] 6 seconds
- [ ] 7 seconds
- [ ] 8 seconds

**Q5. The CPU time formula `IC × CPI × T_clock` shows three independent handles on performance. Increasing clock frequency while keeping IC and CPI constant:**
- [ ] Increases CPU time proportionally.
- [x] Decreases CPU time proportionally (each cycle is shorter).
- [ ] Has no effect because CPI also changes.
- [ ] Only helps for floating-point instructions.

**Q6. Interrupts are preferred over polling for a keyboard input device because:**
- [ ] Interrupts consume less energy per keystroke in absolute terms.
- [x] The CPU can run other tasks between keystrokes rather than burning cycles in a polling loop that rarely finds data ready.
- [ ] Interrupts are simpler to program than polling loops.
- [ ] Polling cannot detect fast input events like keystrokes.
