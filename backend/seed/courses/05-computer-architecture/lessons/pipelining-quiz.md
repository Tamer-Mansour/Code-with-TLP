# Quiz: Pipelining

**Q1. In the classic 5-stage pipeline, which stage writes a result back to the register file?**
- [ ] EX (Execute)
- [ ] MEM (Memory Access)
- [x] WB (Write Back)
- [ ] ID (Instruction Decode)

**Q2. An instruction enters the IF stage in cycle 1. In a 5-stage pipeline with no stalls, in which cycle does it complete WB?**
- [ ] 4
- [x] 5
- [ ] 6
- [ ] 9

**Q3. Forwarding (bypassing) solves most RAW hazards without stalls by:**
- [ ] Predicting the result before the ALU computes it.
- [ ] Reordering instructions at compile time.
- [x] Routing the computed result from a later pipeline register directly to the ALU input of the consuming instruction, bypassing the register file.
- [ ] Executing the dependent instruction speculatively with an estimated value.

**Q4. A load-use hazard requires exactly one stall cycle even with forwarding because:**
- [ ] Load instructions always access the slow data cache.
- [ ] Forwarding is not implemented for load results.
- [x] The load's data is not available until the end of MEM (cycle 4), but the consuming instruction needs it at the start of EX (cycle 4) — one cycle too early, even after a MEM-to-EX forward.
- [ ] The WB stage for loads takes two cycles.

**Q5. A 20-stage pipeline has a branch misprediction penalty of 19 cycles. If 15% of instructions are branches and 5% of them are mispredicted, what is the CPI contribution from branch mispredictions?**
- [ ] 0.015 cycles
- [ ] 0.14 cycles
- [x] 0.143 cycles
- [ ] 0.285 cycles

**Q6. Structural hazards are nearly eliminated in modern CPUs primarily because:**
- [ ] Pipelines have been made shallower over time.
- [x] Separate instruction caches and data caches (Harvard-style L1) remove the most critical resource conflict, and execution units are replicated.
- [ ] Modern CPUs execute only one instruction at a time.
- [ ] Branch prediction eliminates the need for duplicate units.
