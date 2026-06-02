# Quiz: Foundations of Computer Architecture

Test your understanding of the core concepts from this module.

---

**Q1. Which of the following is part of the Instruction Set Architecture (ISA) and NOT part of the microarchitecture?**
- [ ] The number of pipeline stages in the processor
- [ ] The size and associativity of the L1 data cache
- [x] The binary encoding format of instructions
- [ ] Whether the processor uses static or dynamic branch prediction

The ISA defines everything software must know — including instruction encoding. Pipeline depth, cache configuration, and branch predictor type are microarchitecture decisions invisible to correct software.

---

**Q2. A program executes 4 billion instructions on a 2 GHz processor with a measured CPI of 2.0. What is the execution time?**
- [ ] 1 second
- [ ] 2 seconds
- [x] 4 seconds
- [ ] 8 seconds

Execution Time = IC × CPI / f = 4×10⁹ × 2.0 / 2×10⁹ = 4 seconds.

---

**Q3. According to Amdahl's Law, a program has 80% of its execution time in a parallelizable section. If you speed that section up by 4×, what is the overall speedup?**
- [ ] 3.20×
- [x] 2.50×
- [ ] 4.00×
- [ ] 1.80×

Speedup = 1 / ((1 - 0.80) + 0.80/4) = 1 / (0.20 + 0.20) = 1 / 0.40 = 2.50×.

---

**Q4. What distinguishes the Modified Harvard Architecture used in modern CPUs from a pure Von Neumann architecture?**
- [ ] Modified Harvard uses a single unified cache for both instructions and data
- [ ] Modified Harvard has no cache at all — it relies entirely on main memory
- [x] Modified Harvard has separate L1 instruction and data caches but a unified main memory
- [ ] Modified Harvard stores the program counter in a separate memory space

Modern CPUs expose a unified address space (Von Neumann) but use separate L1-I$ and L1-D$ caches inside the chip to allow simultaneous instruction fetch and data access (Harvard advantage).

---

**Q5. Dennard Scaling broke down around 2005 primarily because:**
- [ ] Transistor counts stopped increasing
- [ ] Clock frequencies could not be encoded in the ISA
- [ ] Cache memory became too expensive to manufacture
- [x] Leakage current prevented supply voltage from being reduced further

Dennard Scaling depended on voltage dropping proportionally with feature size. Below ~1 V, leakage current (transistors that leak even when off) made further voltage reduction impractical, causing power density to rise.

---

**Q6. In the abstraction stack from transistors to software, which layer serves as the stable contract between hardware and software?**
- [ ] The operating system kernel
- [ ] The digital logic (gate) layer
- [ ] The high-level language compiler
- [x] The Instruction Set Architecture (ISA)

The ISA is the boundary: everything above it is software, everything below it is hardware. Both compiler writers and hardware designers agree to honour the ISA, allowing hardware implementations to change without breaking existing software.
