# Quiz: The CPU and Datapath

**Q1. What does the Program Counter (PC) hold?**
- [ ] The result of the last ALU operation.
- [x] The memory address of the next instruction to fetch.
- [ ] The current instruction's opcode bits.
- [ ] The stack base address.

**Q2. During the decode phase, the control unit reads `funct7=0100000, funct3=000` with opcode `0110011`. Which operation does this encode in RISC-V?**
- [ ] ADD
- [x] SUB
- [ ] AND
- [ ] SLT

**Q3. A 1-bit ALU computes `Sum = A XOR B XOR CarryIn`. For A=1, B=1, CarryIn=1, the Sum and CarryOut are:**
- [ ] Sum=0, CarryOut=0
- [x] Sum=1, CarryOut=1
- [ ] Sum=0, CarryOut=1
- [ ] Sum=1, CarryOut=0

**Q4. In a single-cycle CPU, why does a RISC-V `AND` instruction still take as long as a `LW` instruction?**
- [ ] AND requires two memory accesses.
- [ ] The register file is shared between instructions.
- [x] The clock period is fixed to the slowest instruction (LW), so all instructions wait for the same period.
- [ ] AND instructions always execute after memory is checked.

**Q5. The `MemToReg` control signal selects:**
- [ ] Whether to read or write the data memory.
- [ ] Which register address to write to.
- [x] Whether the value written back to the register file comes from the ALU result or from data memory.
- [ ] Whether the ALU's second operand is a register or an immediate.

**Q6. Carry-lookahead adders are faster than ripple-carry adders because:**
- [ ] They use fewer transistors per bit.
- [ ] They operate on smaller numbers.
- [x] They compute all carry bits simultaneously in O(log N) gate levels rather than propagating carry serially through N stages.
- [ ] They avoid using XOR gates, which have higher delay.
