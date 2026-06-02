# Quiz: Assembly and Machine Code Basics

**Q1. In a RISC-V RV32I instruction encoded as `0x00430293`, which bit field contains the opcode?**

- [ ] Bits [31:25]
- [ ] Bits [19:15]
- [ ] Bits [11:7]
- [x] Bits [6:0]

Explanation: RISC-V places the 7-bit opcode in the lowest bits [6:0] of every 32-bit instruction word, enabling fast single-cycle decode independent of instruction format.

---

**Q2. What is the primary reason load/store architectures restrict memory access to only LOAD and STORE instructions?**

- [ ] To reduce the number of opcodes needed
- [x] To isolate memory latency and simplify pipeline hazard detection
- [ ] To make programs run faster by always using the cache
- [ ] To enforce alignment checking on all instructions

Explanation: By confining memory access to dedicated instructions, the pipeline knows exactly which operations may stall on cache miss. ALU instructions are guaranteed single-cycle, making pipeline timing predictable and hazard logic simpler.

---

**Q3. In RISC-V, register x0 is hardwired to zero. What happens when a program writes a computed result to x0?**

- [ ] The processor raises an Illegal Instruction exception
- [ ] The result is written to a shadow register accessible only in privileged mode
- [x] The write is silently discarded and x0 continues to read as zero
- [ ] The carry flag is set to indicate the write was ignored

Explanation: Hardwiring x0 to zero eliminates the need for a dedicated ZERO opcode. Hardware ignores write-enable signals to x0, and any read always returns 0.

---

**Q4. A RISC-V B-type (branch) instruction encodes a 13-bit signed offset whose LSB is always 0. Why is the LSB omitted from the instruction encoding?**

- [ ] It saves one bit that is used for the Carry flag
- [ ] Branches can only target even byte addresses in big-endian mode
- [x] All RISC-V instructions are at least 2-byte aligned, so the LSB of any valid target is always 0
- [ ] The assembler sets it to 1 to indicate a taken branch

Explanation: Because instructions are always at least 16-bit (2-byte) aligned, the least-significant bit of any branch target is structurally zero. Omitting it from the encoding effectively doubles the reachable branch range for free.

---

**Q5. Which of the following correctly describes the Fetch-Decode-Execute cycle stage that updates the Program Counter?**

- [ ] Only the Decode stage updates the PC, after identifying the instruction type
- [ ] The Execute stage always increments PC by 4, even for branch instructions
- [x] The Fetch stage increments PC to PC+4 by default; the Execute stage overrides it with a branch target when a branch is taken
- [ ] The PC is updated by an external memory controller, not inside the CPU

Explanation: The PC is speculatively incremented during Fetch. If Execute determines a branch is taken, it overrides the incremented PC with the computed target. On a not-taken branch the speculatively incremented PC remains correct.

---

**Q6. An I-type RISC-V instruction contains a 12-bit immediate field. The field value is `0xFFC` (binary `111111111100`). What signed decimal value does this represent after sign-extension to 32 bits?**

- [ ] 4092
- [ ] 4094
- [x] -4
- [ ] -2

Explanation: `0xFFC` in 12-bit two's complement: the MSB (bit 11) is 1, so the value is negative. Extending: `0xFFFFFFFC` = -4 in 32-bit signed representation.
