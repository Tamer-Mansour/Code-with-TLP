# Quiz: Instruction Set Architecture

**Q1. What is the primary purpose of an Instruction Set Architecture (ISA)?**
- [ ] To describe how transistors are arranged on a chip
- [ ] To define the clock speed of a processor
- [x] To specify the interface between software and hardware, including instructions, registers, and memory model
- [ ] To determine the number of cores in a processor

_The ISA is the abstract machine specification — the hardware-software contract. It says nothing about transistors or clock speeds, which belong to the microarchitecture._

---

**Q2. In RISC-V, which statement about the base integer ISA (RV32I) and extensions is correct?**
- [ ] All extensions are mandatory for any RISC-V implementation
- [x] The base ISA is frozen; new capabilities are added only through optional, versioned extensions
- [ ] Extensions can modify or remove instructions from the base ISA
- [ ] The M extension (multiply/divide) is part of the base RV32I instruction set

_RISC-V's modular philosophy keeps the base ISA permanently stable. Extensions (M, A, F, D, C, V …) are opt-in and never change existing instruction semantics._

---

**Q3. Which addressing mode does RISC-V support for memory load and store instructions?**
- [ ] Scaled index only
- [ ] Absolute (direct) addressing
- [ ] Register indirect (no offset)
- [x] Base register plus signed 12-bit offset

_RISC-V intentionally provides only base+offset addressing for loads and stores. Complex addresses must be computed in separate ALU instructions. This simplifies the decoder and pipeline._

---

**Q4. A program compiled for x86-64 is run on an ARM64 machine without any translation layer. What happens?**
- [ ] It runs correctly because both are 64-bit architectures
- [ ] It runs slowly due to automatic hardware translation
- [x] It fails to execute; the processor raises an illegal-instruction exception
- [ ] It runs correctly if the OS is the same

_Binary machine code is ISA-specific. An ARM64 processor does not know how to decode x86-64 instruction encodings. Without an emulation layer (like Rosetta 2) the binary cannot run._

---

**Q5. What is the key advantage of a three-operand instruction format over a two-operand format?**
- [ ] Three-operand instructions are always shorter in bit length
- [ ] They require less hardware to implement
- [x] The source operands are not overwritten, eliminating false output dependencies
- [ ] They support more addressing modes per instruction

_In a three-operand format (e.g., `add x3, x1, x2`), x1 and x2 are preserved. Two-operand (`add eax, ebx` in x86) overwrites eax, creating a false dependency that out-of-order hardware must rename away._

---

**Q6. In RISC-V, which bits of a 32-bit instruction word always hold the primary opcode field?**
- [ ] Bits [31:25]
- [ ] Bits [19:15]
- [ ] Bits [14:12]
- [x] Bits [6:0]

_The RISC-V spec places the 7-bit primary opcode in bits [6:0] for all 32-bit instruction formats. Keeping opcode and register specifiers (rd, rs1) at fixed positions lets the decoder start reading the register file before it finishes decoding the instruction type._
