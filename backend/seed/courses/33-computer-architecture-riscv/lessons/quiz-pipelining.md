# Quiz: Pipelining and ILP

Test your understanding of the key concepts from this module.

---

**Q1. A 5-stage pipeline runs at 1 GHz (1 ns per cycle). What is the latency of a single instruction compared to a non-pipelined processor with the same 5 ns per instruction?**

- [ ] The pipelined processor has 5x lower latency
- [x] The latency is the same (both 5 cycles / 5 ns)
- [ ] The pipelined processor has 5x higher latency
- [ ] The pipelined processor has 1 ns latency

Pipelining does not reduce per-instruction latency — a single instruction still passes through all k stages. Pipelining improves throughput, not latency. Pipeline register overhead may even add a small amount.

---

**Q2. A 4-stage pipeline has 200 instructions and zero stall cycles. How many total cycles does the program require?**

- [ ] 200
- [ ] 800
- [x] 203
- [ ] 204

Using the formula: total_cycles = (k - 1) + N = (4 - 1) + 200 = 203. The (k-1) = 3 accounts for filling the pipeline before the first instruction completes.

---

**Q3. Which of the following is the PRIMARY reason out-of-order processors use a Re-Order Buffer (ROB)?**

- [ ] To increase the number of physical registers available
- [ ] To rename architectural registers to physical registers
- [x] To commit results to architectural state in program order, enabling precise exceptions
- [ ] To detect data hazards between instructions

The ROB tracks in-flight instructions in program order. Even though instructions execute out-of-order, they commit (retire) from the ROB head in sequence, ensuring precise exceptions and correct branch misprediction recovery.

---

**Q4. A 5-stage pipeline executes 1,000 instructions. 25% of instructions are loads, and each load is immediately followed by a dependent instruction causing a 1-cycle stall. What is the average CPI?**

- [ ] 1.00
- [ ] 1.10
- [x] 1.25
- [ ] 1.50

Average stall cycles per instruction s = 0.25 × 1 = 0.25. CPI = 1 + s = 1.25. The pipeline fill cost is negligible for large N.

---

**Q5. What does "superscalar" mean in processor design?**

- [ ] A processor with more than 5 pipeline stages
- [ ] A processor that uses out-of-order execution
- [x] A processor that fetches and issues multiple instructions per clock cycle
- [ ] A processor with a clock speed exceeding 1 GHz

Superscalar refers specifically to the ability to issue (start executing) more than one instruction per clock cycle by duplicating functional units and using wider fetch/decode logic. Superscalar and out-of-order are independent properties — a processor can be superscalar in-order.

---

**Q6. Register renaming in out-of-order processors primarily eliminates which type of hazard?**

- [ ] Structural hazards caused by too few functional units
- [ ] True data hazards (RAW — Read After Write)
- [x] False dependencies (WAW and WAR hazards) caused by reuse of register names
- [ ] Control hazards caused by branches

Register renaming maps architectural register names to a larger pool of physical registers. This eliminates WAW (Write After Write) and WAR (Write After Read) hazards, which are artifacts of limited architectural register names, not true data flow dependencies.
