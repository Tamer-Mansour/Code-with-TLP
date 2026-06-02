# Quiz: The CPU and Its Components

Test your understanding of the CPU's building blocks, their roles, and how they interact during instruction execution.

---

**Q1. Which component of the CPU generates the control signals that configure muxes, enable register writes, and select ALU operations?**

- [ ] The ALU
- [ ] The register file
- [x] The control unit
- [ ] The memory address register (MAR)

_The control unit decodes the opcode and emits control signals; it does not process data itself._

---

**Q2. In a RISC-V single-cycle datapath, what determines the maximum clock frequency?**

- [ ] The size of the register file
- [x] The propagation delay of the longest combinational path (critical path)
- [ ] The number of instructions in the program
- [ ] The width of the data bus

_The clock period must be at least as long as the critical path delay; shortening the critical path (e.g., via pipelining) allows a higher frequency._

---

**Q3. Writing a value to RISC-V register x0 results in:**

- [ ] An illegal-instruction exception
- [ ] The value being stored normally and readable later
- [x] The value being silently discarded; x0 always reads as zero
- [ ] A memory write to address 0x00000000

_x0 is hardwired to zero in RISC-V; writes have no effect and reads always return 0._

---

**Q4. What is the primary advantage of microprogrammed control over hardwired control?**

- [ ] It is always faster because it uses a ROM
- [ ] It requires fewer transistors
- [x] Instructions can be added or patched by updating the microcode ROM without re-fabricating silicon
- [ ] It eliminates the need for a clock signal

_Microprogrammed control stores control signals in a ROM (control store), making it easy to add new instructions or fix bugs via a microcode update — x86 CPUs use this for Spectre/Meltdown mitigations._

---

**Q5. During the execution of a `lw` (load word) instruction in a multi-cycle CPU, which register holds the data read back from memory before it is written to the register file?**

- [ ] The Instruction Register (IR)
- [ ] The Program Counter (PC)
- [ ] The Memory Address Register (MAR)
- [x] The Memory Data Register (MDR)

_The MDR sits between the data memory port and the register file write port; it latches the memory output so it can be written to the destination register in the write-back stage._

---

**Q6. A RISC-V branch instruction `beq x1, x2, label` is at address 0x1000 and `label` is at address 0x0FF0. What value is encoded as the branch offset in the instruction?**

- [ ] 0x0FF0
- [ ] 0x0010
- [x] -0x10 (i.e., -16 in decimal)
- [ ] -0x08

_The B-type immediate encodes a PC-relative signed byte offset: target − PC = 0x0FF0 − 0x1000 = −0x10 (−16). The instruction encodes this in multiples of 2 bytes (so the stored immediate field is −8), but the assembler handles the conversion automatically._

---
