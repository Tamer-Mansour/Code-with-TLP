# Quiz: Introduction to RISC-V

Test your understanding of the core concepts from this module: what RISC-V is, why it matters, how it is organized, and how to read its naming conventions.

---

**Q1. Which of the following best describes RISC-V?**

- [ ] A specific processor chip sold by RISC-V International.
- [x] An open, royalty-free Instruction Set Architecture specification.
- [ ] A proprietary ISA licensed by UC Berkeley.
- [ ] A variant of the ARM Cortex-M architecture.

RISC-V is a specification — a document defining instructions, registers, and behavior. No chip is called "RISC-V"; processors are implementations of the RISC-V ISA. RISC-V International is a non-profit that governs the specification, not a chip vendor.

---

**Q2. What does the "G" represent in the ISA string RV64GC?**

- [ ] "General" — it means the chip supports all possible extensions.
- [ ] "GPU" — it means the chip includes a graphics unit.
- [x] A shorthand for I + M + A + F + D + Zicsr + Zifencei.
- [ ] "Gigahertz" — it refers to the clock frequency class.

The letter G is a defined shorthand in the RISC-V specification for the combination of the base integer ISA (I), integer multiply/divide (M), atomics (A), single-precision float (F), double-precision float (D), and two mandatory Z-extensions. It is not a generic adjective.

---

**Q3. A company wants to build a RISC-V processor and add custom instructions for AI inference. Which statement is correct?**

- [ ] Custom instructions are forbidden by the RISC-V specification.
- [ ] The company must pay RISC-V International a fee to add custom instructions.
- [x] The RISC-V specification reserves opcode space for custom (X) extensions, which can be added freely.
- [ ] Custom instructions require an ARM architecture license as a prerequisite.

RISC-V explicitly reserves encoding space for non-standard custom extensions, named with an X prefix by convention (e.g., Xvendor_ai). Companies can add proprietary instructions without any approval or fee. This is one of RISC-V's key advantages for application-specific hardware.

---

**Q4. Which of the following is a key difference between RV32I and RV64I?**

- [ ] RV64I has more general-purpose registers than RV32I.
- [ ] RV32I supports floating-point operations but RV64I does not.
- [x] RV64I has 64-bit wide registers and a 64-bit address space; RV32I has 32-bit registers and a 32-bit address space.
- [ ] RV64I is a completely different ISA with a different instruction encoding.

Both RV32I and RV64I have 32 general-purpose registers (x0–x31). The difference is XLEN: the register width and address space. RV64I also adds doubleword loads/stores and W-suffix instructions for 32-bit operations. Floating point is an independent extension (F, D), orthogonal to the XLEN choice.

---

**Q5. Why did RISC-V International move its incorporation from the United States to Switzerland in 2019?**

- [ ] Switzerland has lower corporate taxes.
- [ ] UC Berkeley required the move as a condition of transferring the IP.
- [x] To reduce the risk that US export control regulations could restrict international members' access to the ISA.
- [ ] ARM Holdings lobbied the US government to expel RISC-V Foundation.

US export control laws (EAR, ITAR) can restrict the transfer of technology to certain entities or nations. By incorporating as a Swiss non-profit, RISC-V International operates under a different legal regime, making it harder for geopolitical decisions to selectively block access to the specification — which is important given RISC-V's global membership.

---

**Q6. Which of the following correctly describes the relationship between an ISA and a microarchitecture?**

- [ ] An ISA and a microarchitecture are the same thing — different words for the same concept.
- [ ] A microarchitecture defines the instruction set; an ISA is the physical chip.
- [x] An ISA is the software-visible specification of instructions and behavior; a microarchitecture is one concrete implementation of that ISA in hardware.
- [ ] An ISA can only have one microarchitecture implementation.

The ISA defines the interface — what instructions exist and what they do. A microarchitecture is one way to implement that interface in silicon: specific pipeline stages, cache sizes, execution units. Multiple different microarchitectures can implement the same ISA (e.g., Rocket Chip and BOOM are both RV64GC but have very different internal designs).
