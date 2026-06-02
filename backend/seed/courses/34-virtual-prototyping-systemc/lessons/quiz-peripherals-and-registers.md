# Quiz: Modeling Peripherals and Register Models

Test your understanding of peripheral models, register access semantics, bit-field modeling, and side-effect callbacks.

---

**Q1. A peripheral model's register reads back a value different from what was last written. Which access type most likely explains this?**

- [ ] RW — Read/Write, stores verbatim
- [x] RC — Read to Clear, clears the value on read
- [ ] WO — Write Only, ignores reads
- [ ] RW with a post-write callback

*RC (Read-to-Clear) registers return the current value and simultaneously clear it, so consecutive reads return different values. This is typical for FIFO data registers and latched error counters.*

---

**Q2. Firmware writes `0xFFFFFFFF` to an interrupt status register that is fully W1C. What is the expected result?**

- [ ] The register is set to `0xFFFFFFFF`
- [ ] Nothing changes; writes are ignored on W1C registers
- [x] All bits in the register are cleared to `0x00000000`
- [ ] Only bits that were already set are cleared; the others are set to 1

*W1C semantics: writing 1 to a bit clears it. Writing `0xFFFFFFFF` writes 1 to every bit, so all bits are cleared. Writing 0 to a bit has no effect.*

---

**Q3. A 32-bit register at offset 0x10 has bits [7:4] as W1C and bits [3:0] as RO. Its current value is `0x000000FF`. Firmware writes `0x000000F0`. What is the new register value?**

- [ ] `0x000000F0`
- [ ] `0x0000000F`
- [x] `0x0000000F`
- [ ] `0x000000FF`

*Bits [7:4] are W1C: written value is `0xF0` so all four bits in [7:4] are cleared (0xF0 & 0xF0 = 0xF0, clear those). Bits [3:0] are RO: preserved from current value = `0x0F`. Result = 0x00 | 0x0F = `0x0000000F`.*

---

**Q4. Which SystemC construct is most appropriate for modeling a peripheral's internal state machine that must wait for a timer expiry and then assert an interrupt?**

- [ ] `SC_METHOD` sensitive to a clock edge
- [x] `SC_THREAD` using `wait(sc_time)`
- [ ] A callback function called from `b_transport`
- [ ] A `tlm_initiator_socket` in the peripheral module

*`SC_THREAD` can suspend at `wait(sc_time)` and resume later, naturally modeling the passage of time between starting a transfer and completing it. `SC_METHOD` cannot block; callbacks run synchronously in the bus thread.*

---

**Q5. What is the primary risk of implementing a peripheral's register bank as a plain `uint32_t` array indexed by offset?**

- [ ] Arrays are too slow for simulation
- [ ] The array cannot hold more than 256 registers
- [x] All array accesses behave as RW, losing RO, W1C, and RC semantics
- [ ] TLM sockets cannot address arrays directly

*A plain array stores and returns values verbatim. It cannot enforce that RO fields ignore writes, that W1C bits clear on a one-write, or that RC fields clear on read — all of which are essential for correct firmware behavior.*

---

**Q6. A callback attached to a control register's post-write event fires during the model's `reset()` call, starting a peripheral operation too early. What is the correct fix?**

- [ ] Remove all post-write callbacks from control registers
- [ ] Call `reset()` before constructing the register bank
- [x] Bypass callbacks during reset by using a dedicated reset path that writes directly to the register value without invoking callbacks
- [ ] Use a global flag to suppress all TLM transactions during reset

*The cleanest solution is a `reset()` method that directly writes `reg.value = reg.reset_val` without routing through `write()` (which triggers callbacks). This mirrors real hardware: reset lines bypass normal register-write paths.*
