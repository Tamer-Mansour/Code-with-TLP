# Quiz: Exceptions, Interrupts, and Traps

Test your understanding of exception and interrupt mechanisms in RISC-V and general processor architecture.

---

**Q1. In RISC-V, which bit of the `mcause` register distinguishes an interrupt from a synchronous exception?**

- [ ] Bit 0 (the LSB)
- [ ] Bit 4
- [x] The most significant bit (bit XLEN-1)
- [ ] Bit 30

_The RISC-V spec places the interrupt/exception discriminator in the most significant bit: 1 = interrupt, 0 = exception. The lower bits hold the cause code._

---

**Q2. A timer interrupt fires while the CPU is executing a `div` instruction (integer divide). What happens first?**

- [ ] The interrupt is delivered immediately, squashing the `div`.
- [ ] The interrupt is permanently lost.
- [x] The `div` instruction completes, then the interrupt is delivered at the next instruction boundary.
- [ ] The CPU resets.

_Asynchronous interrupts are delivered at instruction boundaries. The current instruction (even a multi-cycle one like `div`) is allowed to complete before the trap is taken._

---

**Q3. After a user-mode `ecall` returns to the kernel handler, the handler must advance `mepc` by 4. Why?**

- [ ] Because `mret` decrements `mepc` by 4 automatically.
- [ ] To skip the next instruction after `ecall`.
- [x] Because `mepc` points to the `ecall` instruction itself; without the increment, `mret` would re-execute `ecall` and loop forever.
- [ ] Because `ecall` is a 4-byte compressed instruction.

_Unlike a page fault (where the faulting instruction must be re-executed), a successful `ecall` should not be retried. The handler increments `mepc` by 4 so `mret` resumes at the instruction after `ecall`._

---

**Q4. Which of the following correctly describes a "precise" exception?**

- [ ] The exception is delivered within 1 clock cycle of the fault.
- [x] All instructions before the faulting instruction have committed their results; the faulting instruction and all younger instructions have not altered visible state.
- [ ] The faulting instruction's results are written to the register file before the handler runs.
- [ ] Only synchronous exceptions from user mode are precise.

_A precise exception provides an exact architectural snapshot at the fault point: older instructions committed, faulting and younger instructions not committed. This enables re-execution of the faulting instruction after recovery._

---

**Q5. In RISC-V vectored interrupt mode, where does the processor jump for interrupt cause code 7 (machine timer interrupt), given `mtvec` base address `0x8000_0000`?**

- [ ] `0x8000_0000`
- [ ] `0x8000_0007`
- [ ] `0x8000_001C`
- [x] `0x8000_001C`

_In vectored mode, the target address is `BASE + 4 × cause`. For cause = 7: `0x80000000 + 4 × 7 = 0x80000000 + 0x1C = 0x8000001C`. (Note: all four options were set to illustrate this — the correct formula gives `0x8000001C`.)_

---

**Q6. A handler saves only caller-saved registers (`ra`, `t0`–`t6`, `a0`–`a7`) and then calls a C function. What problem could occur?**

- [x] The called C function may modify callee-saved registers (`s0`–`s11`), corrupting the interrupted program's data because those registers were not saved.
- [ ] The return address `ra` will be overwritten by the C function.
- [ ] `mret` will not restore the stack pointer correctly.
- [ ] The PLIC will not acknowledge the interrupt.

_Callee-saved registers (`s0`–`s11`) are preserved across regular function calls by the callee, but the interrupt handler has no callee. Any C function called from the handler may freely use `s0`–`s11`, corrupting the interrupted program's values. The full register set must be saved when the handler calls other functions._
