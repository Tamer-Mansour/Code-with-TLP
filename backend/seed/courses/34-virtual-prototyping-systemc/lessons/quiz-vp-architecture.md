# Quiz: Virtual Platform Architecture

Test your understanding of virtual platform components, topology, and assembly.

---

**Q1. In TLM-2.0, which component acts as BOTH an initiator and a target?**

- [ ] The CPU instruction set simulator (ISS)
- [x] The bus / interconnect router
- [ ] The memory model
- [ ] The peripheral register model

The bus receives transactions from upstream initiators (so it is a target) and forwards them to downstream peripherals (so it is an initiator). The ISS is a pure initiator; memory and peripherals are pure targets.

---

**Q2. What is the correct order of operations in `sc_main` for assembling a VP?**

- [ ] Bind sockets → Instantiate modules → Call `sc_start`
- [ ] Call `sc_start` → Instantiate modules → Bind sockets
- [x] Instantiate modules → Bind sockets → Call `sc_start`
- [ ] Instantiate modules → Call `sc_start` → Bind sockets

Elaboration (instantiation and binding) must be complete before `sc_start` launches the simulation. Binding a socket after `sc_start` is illegal in SystemC and will cause a runtime error.

---

**Q3. Which mechanism allows an ISS to read memory without issuing a `b_transport` call on every access?**

- [ ] `nb_transport_fw`
- [ ] `sc_signal` binding
- [ ] `tlm_fifo`
- [x] Direct Memory Interface (DMI)

DMI provides the ISS with a host-side pointer to the backing array of a memory model. The ISS can then use `memcpy` directly, bypassing the TLM socket overhead for instruction fetches and bulk data reads.

---

**Q4. A platform has two peripherals: UART at base `0x40000000` (size 4 KB) and Timer at base `0x40001000` (size 4 KB). What is the most likely bug if the Timer always reads 0?**

- [ ] The Timer clock frequency is wrong
- [ ] The ROM image is not loaded
- [x] The bus decode table has the wrong base address or size for Timer
- [ ] The CPU reset vector points to RAM instead of ROM

If the Timer's decode range is misconfigured, Timer-addressed transactions are either dropped or forwarded to UART, which responds with UART register values (often 0 at reset). The Timer itself never receives the read transaction.

---

**Q5. Why must a VP assert reset before calling `sc_start`?**

- [ ] To initialize the `sc_clock` frequency
- [ ] To prevent the ISS from fetching instructions before firmware is loaded
- [x] To put all peripherals into a known state matching real hardware power-on behavior
- [ ] To bind any remaining unconnected sockets

Firmware boot code assumes peripherals are in their reset state. If reset is never asserted, peripherals start with random internal state (C++ uninitialized members), which causes subtle bugs that are nearly impossible to reproduce on real hardware.

---

**Q6. Which fidelity level should you choose for a peripheral model when the goal is bare-metal driver development?**

- [ ] Stub — always returns reset values
- [x] Behavioral / Functional — correct register semantics, no timing
- [ ] Timing-accurate — annotated latencies
- [ ] Cycle-accurate — matches RTL cycle-by-cycle

Driver development requires correct register read/write semantics and interrupt behavior but does not need cycle-accurate timing. Functional models run significantly faster than timing-accurate or cycle-accurate models, speeding up firmware iteration.
