# Quiz: Branch Prediction and Speculation

Test your understanding of branch prediction hardware, predictor designs, speculative execution, and security implications.

---

**Q1. In a 5-stage RISC-V pipeline where a branch resolves at the end of the Execute stage (stage 3), how many pipeline stages are wasted on a misprediction?**

- [ ] 1 cycle — only the decode stage is wasted
- [x] 2 cycles — instructions in Fetch and Decode must be flushed
- [ ] 3 cycles — the branch itself plus two following instructions are flushed
- [ ] 0 cycles — the pipeline stalls automatically without wasting slots

The pipeline has already fetched and decoded 2 instructions past the branch before the Execute stage resolves it. Those 2 slots become bubbles.

---

**Q2. A 2-bit saturating counter is in state `11` (Strongly Taken). The next three branch outcomes are: Not-Taken, Not-Taken, Taken. What is the final state?**

- [ ] `00` — Strongly Not-Taken
- [x] `10` — Weakly Taken
- [ ] `01` — Weakly Not-Taken
- [ ] `11` — Strongly Taken

State transitions: `11` → `10` (NT) → `01` (NT) → `10` (T). Final state is `10` (Weakly Taken).

---

**Q3. What is the primary advantage of the BTFN (Backward-Taken, Forward-Not-Taken) static predictor over always-not-taken?**

- [ ] It uses runtime branch history to adapt its prediction
- [ ] It stores branch target addresses in a dedicated buffer
- [x] It correctly predicts loop back-edges as taken, improving accuracy for loops
- [ ] It eliminates the need for a BTB entirely

BTFN exploits the observation that backward branches (loops) are usually taken while forward branches (if/else) are usually not-taken — all without any runtime state.

---

**Q4. In a gshare correlating predictor, the PHT is indexed by which combination?**

- [ ] Branch PC bits only
- [ ] Global History Register bits only
- [x] XOR of Global History Register bits and branch PC bits
- [ ] The sum of the GHR value and the branch PC

Gshare XOR-hashes the GHR with low-order PC bits to distribute entries across the PHT while capturing both address identity and global history context.

---

**Q5. The Return Address Stack (RAS) mispredicts on which of the following patterns?**

- [ ] A normal function call followed by a return
- [ ] A recursive function with bounded recursion depth less than the RAS size
- [x] A `longjmp` that bypasses the normal return path
- [ ] A leaf function that is called exactly once

`longjmp` does not execute the matching `return` instruction, so the RAS entry for the corresponding `call` is never consumed. The RAS falls out of sync, causing mispredictions on subsequent legitimate returns.

---

**Q6. In a Spectre variant 1 attack, what is the role of the CPU cache after the mispredicted speculative execution is squashed?**

- [ ] The cache is automatically flushed along with the ROB on misprediction
- [ ] The cache stores the secret value in architectural memory for the attacker to read
- [x] The cache retains data loaded speculatively, creating a measurable timing side channel
- [ ] The cache prevents the attack by returning stale data during speculation

Rollback restores architectural state (registers, memory writes) but does NOT undo cache fills. The speculatively loaded cache line persists and is detectable via cache-timing measurements like FLUSH+RELOAD.
