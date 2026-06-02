# Quiz: TLM Coding Styles and Timing

**Q1. Which TLM-2.0 API does the Loosely-Timed (LT) coding style use for bus transactions?**
- [ ] `nb_transport_fw` with four explicit phases
- [x] `b_transport` (blocking transport)
- [ ] `get_direct_mem_ptr` for all accesses
- [ ] `tlm_fw_transport_if` with manual phase management

_LT uses the single blocking `b_transport` call, which models an entire transaction in one function call without explicit phase handshaking._

---

**Q2. In the Approximately-Timed (AT) coding style, what does `TLM_UPDATED` returned from `nb_transport_fw` signal to the initiator?**
- [ ] The transaction is complete; no callback will follow
- [ ] The target rejected the request; retry later
- [x] The phase and/or delay parameter was modified; act on the updated values
- [ ] The target requires a direct memory interface instead

_`TLM_UPDATED` means the target has changed the `phase` or `t` argument in-place. The initiator must read those updated values to know the next step. `TLM_COMPLETED` (not `TLM_UPDATED`) means the transaction is done._

---

**Q3. An initiator using temporal decoupling runs 800 ns ahead of the global simulation time (quantum = 1 µs). Which statement is correct?**
- [ ] The initiator will never synchronize because it has not yet reached the quantum
- [x] The initiator will synchronize at or after the next transaction that pushes local time to 1000 ns or more
- [ ] All other threads immediately see the initiator's writes at 800 ns local time
- [ ] The global clock automatically advances every nanosecond regardless of the quantum

_Temporal decoupling delays synchronization until the local time offset reaches the quantum (1000 ns here). Other threads see only global simulation time, not the initiator's local time._

---

**Q4. What does the `tlm_quantumkeeper::sync()` method do?**
- [ ] Resets only the local time to zero without advancing the global clock
- [ ] Signals the target that the initiator is ready for the next transaction
- [ ] Sets the global quantum for all quantumkeeper instances
- [x] Calls `wait(local_time)` to advance the global clock, then resets local time to zero

_`sync()` is exactly `wait(local_time); reset()` — it flushes the accumulated local offset into the global simulation time and starts the local counter fresh._

---

**Q5. In the AT four-phase protocol, which phase signals that the target has accepted the request and the initiator may issue the next transaction?**
- [ ] BEGIN_REQ
- [x] END_REQ
- [ ] BEGIN_RESP
- [ ] END_RESP

_END_REQ is the target's acknowledgment that it has latched the request. After receiving END_REQ, the initiator is free to issue another request — this is how pipelining is modeled in AT._

---

**Q6. A team needs to model a DDR4 memory controller where up to eight read transactions can be outstanding simultaneously. Which coding style is most appropriate?**
- [ ] LT with zero-delay targets, because DDR4 is fast
- [ ] Cycle-accurate RTL simulation for all components
- [x] AT, because it models pipelined overlap of multiple outstanding transactions
- [ ] LT with a 1 µs quantum, because temporal decoupling is sufficient

_AT's phase protocol — specifically the separation between END_REQ and BEGIN_RESP — allows multiple transactions to be in flight simultaneously, which is essential to model DDR4 rank pipelining and command scheduling._
