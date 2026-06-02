# Quiz: VP vs RTL vs Hardware Synthesis

Test your understanding of where Virtual Prototypes fit relative to RTL, Design Verification, and real hardware.

---

**Q1. Which simulation level is the fastest for executing software workloads, and why?**

- [ ] Gate-level simulation, because it models every transistor switching event
- [ ] RTL simulation, because it is the closest to real hardware behavior
- [x] Functional ISS, because it has no time model — only register and memory updates
- [ ] Approximately-timed TLM VP, because it uses temporal decoupling

_Explanation: A functional ISS (e.g., QEMU) executes guest instructions by JIT-compiling them to host instructions with no event queue, no latch propagation, and no time tracking — this is what makes it 100–1000× faster than RTL._

---

**Q2. A VP is submitted as the sole verification artifact for an SoC tapeout sign-off. What critical capability is missing?**

- [ ] The VP cannot boot Linux
- [ ] The VP does not support RISC-V ISA
- [x] The VP has no X-state propagation, no SVA assertions, and cannot produce a coverage database for DV closure
- [ ] The VP cannot model SRAM correctly

_Explanation: DV sign-off requires SVA property checking, constrained-random coverage closure, and X-propagation analysis — none of which are available in a SystemC/TLM VP._

---

**Q3. Which of the following tasks can a VP perform that an FPGA prototype CANNOT?**

- [ ] Running at real-time clock frequency
- [x] Simulating a system at 1000× real-time speed for long-duration regression test campaigns
- [ ] Interfacing with a real DDR4 DRAM module
- [ ] Exercising physical I2C bus transactions

_Explanation: FPGA prototypes run at real-time (MHz range) which makes long regression runs slow. A VP can run at 10–1000× the simulated clock frequency relative to wall-clock time, making it ideal for large regression suites._

---

**Q4. A driver works correctly on the VP but fails on silicon. Which of the following is the MOST likely root cause?**

- [ ] The VP's RISC-V ISA model has a bug
- [x] A timing assumption in the driver — such as a status flag being checked one cycle too early — that the VP's stub accepted silently but RTL enforces correctly
- [ ] The VP uses a different C++ compiler than the target toolchain
- [ ] FreeRTOS does not run on VPs

_Explanation: VPs frequently accept register accesses that violate hardware timing (e.g., reading a status bit before the hardware has had time to set it). The VP stub sets the bit immediately; RTL respects the actual latency._

---

**Q5. What is the primary purpose of using a VP as part of a UVM verification environment?**

- [ ] To replace the RTL DUT entirely
- [ ] To run formal property checking against SystemC properties
- [x] To serve as a transaction-accurate golden reference model inside a UVM scoreboard
- [ ] To generate constrained-random stimulus sequences

_Explanation: The VP's functional accuracy makes it an excellent scoreboard reference: every transaction sent to the RTL DUT is also sent to the VP, and the scoreboard flags any output mismatch._

---

**Q6. An SoC architect wants to estimate memory bandwidth utilization for three candidate bus topologies (ring, crossbar, shared bus) before RTL coding begins. Which model is the most appropriate?**

- [ ] Gate-level netlist simulation with DRAM timing annotation
- [ ] Full RTL simulation of the chosen topology
- [x] Approximately-timed TLM VP with a parameterized interconnect model
- [ ] Functional ISS with no memory model

_Explanation: AT-TLM VPs can model bus topologies at the transaction level, measuring bandwidth and latency under synthetic workloads in seconds rather than weeks. They are specifically designed for pre-RTL architecture exploration._
