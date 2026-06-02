# Quiz: Pipeline Hazards and Mitigation

**Q1. Which type of data hazard occurs when an instruction tries to read a register that a preceding instruction has not yet finished writing?**

- [ ] WAR (Write After Read)
- [ ] WAW (Write After Write)
- [x] RAW (Read After Write)
- [ ] Structural hazard

RAW (Read After Write) is the true dependency — the consumer instruction genuinely needs the value produced by the preceding instruction, which has not yet been written to the register file.

---

**Q2. In a classic five-stage RISC-V pipeline with full forwarding, how many stall cycles does a load instruction followed immediately by an instruction that uses the loaded register require?**

- [ ] 0 stall cycles — forwarding resolves it completely
- [x] 1 stall cycle — forwarding cannot bridge the load-use timing gap
- [ ] 2 stall cycles — the result is not available until WB
- [ ] 3 stall cycles — memory latency adds extra penalty

The load-use hazard always requires exactly 1 stall cycle. The load result is not available until the end of the MEM stage, which is one cycle too late for the consumer's EX stage even with forwarding.

---

**Q3. What is the primary purpose of forwarding (bypassing) in a pipelined processor?**

- [ ] To eliminate all pipeline hazards including control hazards
- [ ] To increase the clock frequency by shortening the critical path
- [x] To route a computed result directly from a pipeline register to the ALU input, avoiding a stall
- [ ] To detect structural hazards and insert bubbles

Forwarding routes the result from the EX/MEM or MEM/WB pipeline register directly to the ALU input of the consuming instruction, eliminating the wait for the value to be written to and read from the register file.

---

**Q4. A structural hazard is best described as:**

- [ ] Two instructions requiring the same register value simultaneously
- [ ] A branch instruction whose target is unknown at fetch time
- [x] Two instructions in different pipeline stages competing for the same hardware resource
- [ ] An instruction being stalled because its source register is not yet written

Structural hazards arise from insufficient hardware — the same physical resource (e.g., a unified memory or a single-port register file) is demanded by two pipeline stages at the same time.

---

**Q5. In a five-stage pipeline where branch resolution occurs in the EX stage, what is the branch penalty if the branch is taken?**

- [ ] 0 cycles — branch prediction eliminates the penalty
- [ ] 1 cycle — only the instruction in ID must be flushed
- [x] 2 cycles — the instructions fetched in IF and ID must be flushed
- [ ] 3 cycles — IF, ID, and EX all fetch wrong instructions

By the time EX resolves the branch (cycle 3 for the branch), the pipeline has already fetched the next instruction in IF (cycle 2) and the one after in ID (cycle 3). Both must be flushed, costing 2 cycles.

---

**Q6. Which compiler technique eliminates the load-use stall by placing an independent instruction between the load and its consumer?**

- [ ] Loop unrolling
- [ ] Constant folding
- [ ] Dead code elimination
- [x] Instruction scheduling (load scheduling)

Instruction scheduling (also called load scheduling) reorders instructions so that an independent operation fills the one-cycle slot between a load and its first consumer, eliminating the load-use stall penalty without any hardware interlock firing.
