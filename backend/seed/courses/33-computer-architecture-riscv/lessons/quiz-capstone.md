# Quiz: Virtual Prototyping and Interview Capstone

**Q1. Which statement best describes the primary advantage of a virtual prototype over an FPGA prototype?**

- [ ] A virtual prototype is always more cycle-accurate than an FPGA prototype.
- [x] A virtual prototype enables software development before RTL or physical hardware exists.
- [ ] A virtual prototype runs faster than FPGA execution in all cases.
- [ ] A virtual prototype eliminates the need for regression testing.

A virtual prototype models hardware in software, letting firmware teams begin months before tape-out. FPGAs require RTL to exist and boards to be built, making them later in the design flow.

---

**Q2. A developer needs to boot a full Linux kernel on a RISC-V platform model as quickly as possible to verify that a new device driver compiles and loads. Which tool is the best first choice?**

- [ ] gem5 with the O3CPU model in full-system mode.
- [ ] Spike with the proxy kernel (pk).
- [x] QEMU with the `virt` machine type in full-system mode.
- [ ] A SystemC TLM approximately-timed model with RTL co-simulation.

QEMU uses JIT binary translation and runs at 10-100 MIPS, making it the fastest option for booting a full OS. Spike does not support a full OS kernel directly. gem5 in O3 mode is too slow for initial bringup.

---

**Q3. In RV32I instruction encoding, the 12-bit immediate in an I-type instruction is located at bits [31:20]. A friend extracts it with `imm = (instr >> 20) & 0xFFF` but gets wrong results for negative immediates in loads. What is missing?**

- [ ] The immediate should be zero-extended to 32 bits.
- [ ] The mask should be `0x7FF` to remove the sign bit.
- [x] The immediate must be sign-extended from 12 bits to 32 bits before use.
- [ ] The immediate is stored in two separate fields and must be reassembled.

RISC-V immediates are always sign-extended. For I-type, bit 31 of the instruction is the sign bit of the immediate. Masking with `0xFFF` keeps the 12-bit value but does not propagate the sign into the upper 20 bits, causing incorrect negative offsets.

---

**Q4. In TLM-2.0 loosely-timed (LT) modeling, what is the purpose of the `sc_time delay` parameter passed by reference to `b_transport`?**

- [ ] It specifies how long the initiator should sleep on the host OS.
- [ ] It is the absolute simulation time at which the transaction started.
- [x] It is an annotated delay that the initiator adds to its local time to model transaction latency without actually stalling simulation.
- [ ] It forces the SystemC kernel to advance time to that value before returning.

In LT modeling, the delay is a local time annotation. The initiator accumulates the delay and periodically calls `wait(delay)` to synchronise with the SystemC kernel. This avoids context-switching overhead for every transaction, which is why LT models run much faster than AT models.

---

**Q5. Which RISC-V CSR holds the return address that the hardware saves when a trap (exception or interrupt) occurs in M-mode?**

- [ ] `mscratch`
- [ ] `mtvec`
- [x] `mepc`
- [ ] `mcause`

`mepc` (Machine Exception Program Counter) is written by hardware with the address of the instruction that caused the trap (or the next instruction for interrupts). `mret` restores execution from `mepc`. `mtvec` holds the trap handler address. `mcause` encodes the trap reason.

---

**Q6. A cycle-accurate gem5 simulation of a RISC-V core reports CPI = 2.1 for a loop-heavy workload. The team suspects load-use hazards. Which micro-architectural change would most directly reduce the CPI caused by load-use stalls?**

- [ ] Increasing the number of physical registers for register renaming.
- [ ] Adding a larger branch target buffer (BTB).
- [x] Adding out-of-order execution with a load queue so independent instructions can execute during a load-use stall.
- [ ] Switching from a 4-way set-associative cache to a fully associative cache.

Load-use hazards stall the pipeline for one cycle because the loaded value is not available until after the MEM stage, which is too late for the next instruction's EX stage. Out-of-order execution allows the processor to issue other independent instructions during that cycle instead of inserting a bubble, directly reducing effective CPI.
