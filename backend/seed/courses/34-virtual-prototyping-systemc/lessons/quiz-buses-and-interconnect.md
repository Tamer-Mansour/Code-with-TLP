# Quiz: Modeling Buses and Interconnect

**Q1. In a TLM-2.0 bus model, why must the bus subtract the region base address before forwarding a transaction to a target?**

- [ ] To reduce the size of the address field in the transaction payload.
- [x] Because targets expect addresses relative to their own base (target-local), not the global SoC address.
- [ ] To comply with the TLM-2.0 standard, which mandates zero-based addressing for all sockets.
- [ ] To prevent 64-bit overflow when the target performs its internal address decode.

_Targets are unaware of their location in the global map. Stripping the base converts a global address to the target-local offset the target expects._

---

**Q2. Which of the following is the primary reason AXI supports five separate channels (AW, W, B, AR, R)?**

- [ ] To allow the use of different clock frequencies on each channel.
- [ ] To reduce pin count by multiplexing address and data on different wires.
- [x] To enable pipelined, out-of-order transactions where addresses and data can flow independently.
- [ ] To separate read and write traffic onto physically different buses for thermal reasons.

_Separate channels decouple address issuance from data transfer and response, enabling multiple outstanding transactions and out-of-order completion via transaction IDs._

---

**Q3. A round-robin arbiter serves masters 0, 1, and 2 in a 3-master bus. After granting master 1, which master does the arbiter check FIRST for the next grant?**

- [ ] Master 0 (restart from the beginning)
- [ ] Master 1 (same master, if it has another request)
- [x] Master 2 (next in round-robin order after master 1)
- [ ] The master with the lowest arrive_time among all pending requests

_Round-robin advances the `next` pointer to `(granted + 1) % N`, so after granting master 1, the next scan starts at master 2._

---

**Q4. In a TLM loosely-timed (LT) model, how is bus latency typically communicated to the initiator?**

- [ ] By blocking the `b_transport()` call with `wait()` inside the bus model for the exact latency duration.
- [ ] By setting a latency field in the `tlm_generic_payload` response status.
- [x] By accumulating the latency in the `sc_time& delay` parameter passed through `b_transport()`.
- [ ] By sending a separate latency event over an `sc_signal<sc_time>` port.

_In LT, the convention is to accumulate delay in the `delay` parameter. The initiator calls `wait(delay)` at a convenient point (a quantum boundary), amortizing context switches for speed._

---

**Q5. An AXI-to-APB bridge receives a single AXI transaction for 16 bytes. The APB bus is 32 bits (4 bytes) wide. How many APB transactions will the bridge issue?**

- [ ] 1 (the bridge packs all 16 bytes into one APB burst)
- [ ] 2 (APB supports up to 8-byte transfers)
- [ ] 3
- [x] 4 (16 bytes ÷ 4 bytes per APB access = 4 sequential accesses)

_APB is non-pipelined and 32-bit; each access transfers exactly 4 bytes. A 16-byte AXI transaction must be split into 4 individual APB accesses._

---

**Q6. What is the key architectural advantage of a crossbar over a shared bus for a design with 8 masters and 8 targets?**

- [ ] A crossbar uses less area and power than a shared bus at 8 masters.
- [ ] A crossbar eliminates the need for any arbitration logic.
- [x] A crossbar allows up to 8 simultaneous transactions when each targets a different slave, whereas a shared bus allows only 1 at a time.
- [ ] A crossbar supports longer burst lengths than a shared bus.

_A crossbar provides per-target isolation: as long as masters access different targets, all transactions proceed in parallel. A shared bus serializes all traffic regardless of target._
