# Quiz: SystemC Fundamentals

Test your understanding of the SystemC library, its design model, and core concepts from this module.

---

**Q1. What is the correct entry point for a SystemC program?**

- [ ] `int main(int argc, char* argv[])`
- [x] `int sc_main(int argc, char* argv[])`
- [ ] `void sc_start(int argc, char* argv[])`
- [ ] `SC_MODULE(Top)` with `SC_CTOR`

The SystemC library provides its own `main` that initializes the simulation kernel and then calls `sc_main`. Defining `main` yourself causes a linker error (duplicate symbol).

---

**Q2. During which phase does port binding (e.g., `dut.clk(clk_sig)`) occur?**

- [x] Elaboration phase, before `sc_start()` is called
- [ ] Simulation phase, during the first delta cycle
- [ ] Post-simulation, after `sc_stop()` returns
- [ ] Inside `SC_CTHREAD` processes at time 0

Port binding must happen during elaboration. Once `sc_start()` is called the port hierarchy is frozen, and binding after that point is illegal.

---

**Q3. Which SystemC data type would you choose to model a 12-bit unsigned hardware counter with arithmetic operations?**

- [ ] `sc_bv<12>`
- [ ] `sc_lv<12>`
- [x] `sc_uint<12>`
- [ ] `uint16_t`

`sc_uint<12>` provides exactly 12-bit precision with correct wrapping arithmetic and bit-select operators. `sc_bv` supports no arithmetic; `uint16_t` does not wrap at 12 bits.

---

**Q4. What does a delta cycle represent in a SystemC simulation?**

- [ ] One clock period of the fastest registered `sc_clock`
- [ ] A 1 ns time step enforced by the kernel
- [x] A zero-time evaluation step used to propagate signal changes before advancing simulated time
- [ ] The time between two consecutive calls to `sc_start()`

Delta cycles let combinational signal updates settle (mirroring RTL propagation) without advancing simulated time. Multiple delta cycles can occur at the same `sc_time_stamp()`.

---

**Q5. Which macro registers a function as a combinational process that re-executes whenever a signal in its sensitivity list changes?**

- [ ] `SC_THREAD`
- [ ] `SC_CTHREAD`
- [x] `SC_METHOD`
- [ ] `SC_PROCESS`

`SC_METHOD` registers a process that runs to completion (no `wait()` allowed) each time a sensitive signal changes — analogous to a Verilog `always @(...)` combinational block. `SC_THREAD` and `SC_CTHREAD` support suspension via `wait()`.

---

**Q6. TLM-2.0 (Transaction-Level Modeling 2.0) is best described as:**

- [ ] A replacement for SystemC that does not require C++
- [ ] An RTL coding style enforced by IEEE 1666-2011
- [x] A standard communication framework (generic payload, initiator/target sockets) for high-speed system-level simulation
- [ ] A synthesis subset of SystemC supported by all EDA vendors

TLM-2.0 defines `tlm_generic_payload`, blocking/non-blocking transport interfaces, and initiator/target sockets. It enables interoperable, high-speed virtual platforms without modeling every bus signal — the foundation of modern virtual prototyping.
