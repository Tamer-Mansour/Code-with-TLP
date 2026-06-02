# Quiz: RISC vs CISC

Test your understanding of the RISC and CISC design philosophies, their trade-offs, and how they manifest in real ISAs.

---

**Q1. Which of the following is a defining characteristic of a RISC architecture?**

- [ ] Instructions can read operands directly from memory addresses
- [ ] Instruction length varies from 1 to 15 bytes
- [x] All arithmetic instructions operate only on registers (load-store model)
- [ ] A microcode ROM is used to implement complex instructions

_In RISC architectures, only dedicated load and store instructions access memory; arithmetic operates exclusively on registers. This is the load-store model that enables clean, predictable pipelining._

---

**Q2. What is the primary purpose of translating x86 CISC instructions into micro-ops inside a modern Intel or AMD processor?**

- [ ] To reduce the number of instructions executed per program
- [ ] To maintain backward compatibility with 16-bit DOS software
- [x] To enable a wide, out-of-order RISC-style execution back-end despite a CISC ISA
- [ ] To compress the instruction stream and reduce I-cache usage

_Micro-op translation allows the simple, uniform RISC-like operations needed by a modern out-of-order execution engine, while the CISC x86 ISA is preserved at the software interface for compatibility._

---

**Q3. A processor uses 32-bit fixed-length instructions. Which of the following is a direct consequence of this choice?**

- [ ] Each instruction can encode a full 32-bit immediate operand
- [x] The starting address of the next instruction is always PC + 4, enabling simple parallel fetch
- [ ] The instruction set must have exactly 32 instructions
- [ ] All instructions execute in exactly 32 clock cycles

_Fixed instruction width means instruction boundaries are trivially computed: next = current + 4. This eliminates the serial length-scanning problem of variable-length encoding and allows parallel fetch and decode._

---

**Q4. Which ISA feature allows x86 programs to have higher code density than equivalent RISC-V programs?**

- [ ] x86 has 32 general-purpose registers vs. RISC-V's 16
- [ ] x86 executes each instruction in a single clock cycle
- [x] x86 uses variable-length instructions, allowing common operations to encode in as few as 1-2 bytes
- [ ] x86 compilers perform more aggressive loop unrolling

_x86's variable-length encoding lets frequent instructions (like NOP, PUSH, short branches) occupy only 1-2 bytes, while RISC-V standard instructions are always 4 bytes. This produces denser x86 binaries._

---

**Q5. A microcontroller must run on a coin-cell battery for 5 years. Which ISA property most directly supports this goal?**

- [ ] A large number of complex addressing modes
- [ ] Backward compatibility with legacy binaries
- [ ] A large, dense instruction set covering many operations
- [x] Simple decode logic that can be power-gated efficiently when the core is idle

_Power gating — shutting off logic blocks when idle — is more effective on simple RISC cores because the decoder and control logic are smaller and simpler. Complex CISC decoders have higher static leakage and take longer to power up from sleep, making deep sleep less efficient._

---

**Q6. The RISC-V "C" (Compressed) extension addresses which weakness of pure fixed-length RISC designs?**

- [ ] Lack of floating-point support
- [ ] Inability to perform atomic memory operations
- [x] Poor code density compared to variable-length CISC encodings
- [ ] Missing support for privilege levels and operating system interfaces

_The C extension defines 16-bit compressed versions of the most common RISC-V instructions, reducing binary size by roughly 25-30%. Bits [1:0] of each 16-bit word distinguish compressed instructions from standard 32-bit instructions, keeping decode logic simple._
