# Quiz: Modeling the CPU

**Q1. What is the primary difference between an ISS and a cycle-accurate CPU model?**

- [ ] An ISS can only simulate single-core processors; a cycle-accurate model supports multi-core.
- [x] An ISS simulates only the instruction-set architecture without timing; a cycle-accurate model simulates pipeline stages and cache behavior on a cycle-by-cycle basis.
- [ ] An ISS requires RTL source code; a cycle-accurate model works from the ISA specification only.
- [ ] An ISS is always faster than a cycle-accurate model only for floating-point workloads.

_An ISS provides functional correctness — the right register values — at very high speed. A cycle-accurate model adds timing fidelity (IPC, stalls, cache misses) at the cost of 100x–1000x slower simulation._

---

**Q2. In a RISC-V machine-mode CPU model, which register holds the address the CPU will return to after executing `mret`?**

- [ ] `mtvec`
- [ ] `mcause`
- [x] `mepc`
- [ ] `mtval`

_`mepc` (Machine Exception Program Counter) is loaded with the faulting or interrupted PC when a trap is taken. `mret` sets `pc = mepc` to return to that address._

---

**Q3. What does TLM-2.0 Direct Memory Interface (DMI) optimization achieve in an ISS?**

- [ ] It lets the ISS share its register file with the host OS kernel for zero-copy debugging.
- [ ] It replaces `b_transport` with a faster interrupt-driven protocol for peripheral access.
- [x] It gives the ISS a raw host pointer to a memory region, eliminating the `b_transport` call overhead for repeated accesses to that region.
- [ ] It enables the ISS to DMA data directly from the network interface without CPU involvement.

_After a successful transaction, the target can grant DMI access — a raw `uint8_t*` pointer valid for an address range. Instruction fetch from ROM via DMI costs only a pointer dereference instead of a full socket call._

---

**Q4. Which of the following best describes a JIT-based ISS compared to an interpreted ISS?**

- [ ] A JIT ISS translates the entire guest program to host code at startup, then runs it; an interpreted ISS re-translates on every run.
- [ ] A JIT ISS is simpler to implement but runs at the same speed as an interpreted ISS.
- [x] A JIT ISS translates basic blocks of guest instructions to host native code on first execution and caches the result, achieving higher throughput at the cost of greater implementation complexity and the need to handle self-modifying code.
- [ ] A JIT ISS always requires an operating system on the host; an interpreted ISS can run bare-metal.

_JIT compilation amortizes translation cost across many executions of the same basic block. The main engineering challenges are building the code generator back-end and detecting self-modifying code that invalidates cached translations._

---

**Q5. In the fetch-execute loop with temporal decoupling, what is the purpose of the `quantum`?**

- [ ] It limits the maximum number of instructions the ISS can execute before it must flush its pipeline.
- [ ] It sets the maximum simulated address space the ISS can access.
- [x] It controls how far ahead of SystemC simulation time the ISS may run before calling `wait()` to synchronize, trading interrupt-delivery accuracy for faster simulation.
- [ ] It defines the cache line size used by the ISS for DMI-based instruction fetch.

_A larger quantum means fewer `wait()` calls and faster simulation, but interrupts can only be delivered at quantum boundaries, making their simulated timing less accurate. A smaller quantum improves timing accuracy at the cost of more scheduler overhead._

---

**Q6. What must a CPU model do when the TLM interconnect returns `TLM_ADDRESS_ERROR_RESPONSE` for a data load instruction?**

- [ ] Retry the transaction with a smaller data length.
- [ ] Silently return zero to the destination register.
- [ ] Halt the ISS immediately and terminate simulation.
- [x] Raise the appropriate machine exception (e.g., Load Access Fault in RISC-V), saving the faulting address in `mtval` and redirecting the PC to the trap vector.

_A bus error on a load is a fault — the ISS must model the hardware exception mechanism: save PC into `mepc`, set `mcause` to Load Access Fault, store the bad address in `mtval`, and jump to `mtvec`. Silently returning zero would hide memory-map bugs._
