# Quiz: Instruction Set Architecture

**Q1. What is the defining property of a RISC "load/store architecture"?**
- [ ] All instructions are exactly 16 bits wide.
- [x] Only dedicated load and store instructions access memory; all arithmetic and logic operate only on registers.
- [ ] The CPU uses fewer registers than CISC.
- [ ] The ISA supports no floating-point instructions.

**Q2. In RISC-V, register `x0` (zero) always reads as 0 because:**
- [ ] The OS resets it each context switch.
- [ ] It is physically the same as the stack pointer.
- [x] It is hardwired to 0 in hardware; any write to x0 is silently discarded.
- [ ] The assembler replaces reads of x0 with the immediate 0.

**Q3. A RISC-V I-type instruction encodes a 12-bit signed immediate. The maximum positive value representable is:**
- [ ] 4095
- [x] 2047
- [ ] 1023
- [ ] 255

**Q4. The instruction `slli t0, t1, 2` in RISC-V computes:**
- [ ] t0 = t1 >> 2  (logical right shift)
- [ ] t0 = t1 / 4
- [x] t0 = t1 << 2  (logical left shift, equivalent to t1 × 4)
- [ ] t0 = t1 + 2

**Q5. Modern x86 CPUs translate CISC instructions into RISC-like micro-ops (µops) because:**
- [ ] The x86 ISA was designed after RISC-V and must be backward-compatible.
- [x] The internal execution engine is simpler and faster with fixed-format µops, while the x86 ISA surface is maintained for software compatibility.
- [ ] µops allow the CPU to use fewer registers.
- [ ] CISC instructions run directly on the execution units without translation.

**Q6. PC-relative addressing is preferred for branch targets because:**
- [x] The branch offset is small and fixed, making the instruction position-independent — the same binary works regardless of where it is loaded in memory.
- [ ] It is faster than register indirect addressing.
- [ ] Absolute addresses would overflow the 32-bit instruction word.
- [ ] x86 does not support any other form of branch addressing.
