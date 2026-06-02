# Quiz: HW/SW Co-Simulation Concepts

Test your understanding of the key concepts from this module.

---

**Q1. In a TLM-2.0 loosely-timed (LT) model, what is the correct way for an initiator to account for transport delay without blocking simulation time?**

- [ ] Call `sc_stop()` until the delay expires
- [ ] Use `nb_transport_fw()` with the `BEGIN_RESP` phase
- [x] Annotate the delay in the `sc_time` argument of `b_transport()` and then call `wait(delay)` after the call returns
- [ ] Set the `sc_time` argument to `SC_ZERO_TIME` and advance simulation time manually with `sc_core::sc_time_stamp()`

*In LT style, the initiator adds the transport delay to the `sc_time` parameter and calls `wait(delay)` after `b_transport` returns. This lets the target respond instantly (non-blocking in simulation time) while the initiator accounts for the delay locally — the key to high simulation throughput.*

---

**Q2. Which of the following is the PRIMARY purpose of `tlm_quantumkeeper` in a co-simulation ISS?**

- [ ] To enforce a maximum transaction size in TLM payloads
- [ ] To manage the target-side socket binding during elaboration
- [x] To track the ISS's local time budget and trigger `wait()` calls only when the quantum expires, avoiding a context switch on every instruction
- [ ] To convert big-endian target data to little-endian host byte order

*`tlm_quantumkeeper` accumulates simulated time locally inside the ISS loop and issues a single `wait()` per quantum rather than per instruction. This dramatically reduces scheduler overhead and is central to achieving hundreds-of-MIPS throughput.*

---

**Q3. A firmware engineer reports that their RTOS tick ISR (period = 500 µs) is never called during co-simulation. The platform uses an LT ISS with a global quantum of 1 ms. What is the most likely cause?**

- [ ] The TLM router is dropping MMIO writes to the SysTick register
- [ ] The ISS is using big-endian byte order for the vector table
- [x] The global quantum (1 ms) is larger than the interrupt period (500 µs), so the ISS never synchronises often enough to observe the interrupt
- [ ] The GDB stub is holding the simulation paused

*When the quantum is larger than the interrupt period, the ISS runs past the interrupt event without ever calling `wait()` and seeing the signal change. The fix is to set the global quantum to less than or equal to the shortest interrupt period — in this case, under 500 µs.*

---

**Q4. You integrate a Verilog AES block into a SystemC virtual platform using Verilator. What does Verilator NOT model, potentially hiding simulation-only bugs?**

- [ ] Synchronous reset behaviour
- [ ] Multi-cycle pipeline stages
- [x] Unknown (X) signal propagation
- [ ] Clock enable gating

*Verilator compiles synthesisable Verilog to C++ and collapses X values to either 0 or 1 deterministically. Bugs that depend on undriven signal X-propagation are hidden in Verilator simulation but may surface in RTL gate-level simulation or on silicon.*

---

**Q5. In the context of HW/SW co-simulation abstraction levels, which statement correctly describes the Approximately Timed (AT) coding style?**

- [ ] AT models use `b_transport()` with a zero-time delay and no blocking
- [ ] AT models run at gate level and track every flip-flop transition
- [ ] AT models annotate delays but never model back-pressure or bus pipelining
- [x] AT models use a four-phase `nb_transport` handshake (BEGIN_REQ, END_REQ, BEGIN_RESP, END_RESP) to model pipelined bus transactions with accurate back-pressure

*AT is the TLM-2.0 coding style between LT and cycle-accurate. It uses `nb_transport_fw` and `nb_transport_bw` with the four standard phases to correctly model bus pipelining, out-of-order completion, and flow control — making it suitable for DMA bandwidth analysis and memory controller tuning.*

---

**Q6. Which combination of tools represents a fully open-source (no commercial licence required) co-simulation stack for an ARM Cortex-M firmware project?**

- [ ] ARM Fast Models ISS + Synopsys Virtualizer + Cadence Xcelium
- [x] QEMU (ISS) + Verilator (RTL) + Accellera SystemC reference simulator
- [ ] Imperas OVP (ISS) + Siemens Questa + ARM Fast Models
- [ ] Carbon SoC Designer + Synopsys VCS + ARM Fast Models

*QEMU is open-source (GPLv2), Verilator is open-source (LGPL), and the Accellera SystemC reference implementation is freely available. This combination covers ISS execution, RTL simulation, and the SystemC kernel without any commercial licences.*
