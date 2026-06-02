# Quiz: RTL vs Transaction-Level Modeling

Test your understanding of the conceptual leap from signal-level RTL to transaction-level modeling and the trade-offs between them.

---

**Q1. What is the primary unit of communication in a TLM Loosely Timed model?**

- [ ] A clock edge triggering signal updates
- [x] A function call carrying a generic payload with an annotated delay
- [ ] A sequence of individual bit transitions on a bus wire
- [ ] A VHDL port map connecting component signals

In TLM-LT, `b_transport()` carries the entire logical operation in one call. Signal transitions and handshakes are not simulated; a `sc_time` delay annotation approximates the cost.

---

**Q2. Which of the following details is preserved in a TLM model but NOT in an RTL model?**

- [ ] Individual handshake signal transitions (AWVALID, AWREADY)
- [ ] Sub-cycle propagation delays from gate logic
- [x] The functional data values transferred between initiator and target
- [ ] Bus arbitration cycles when two masters compete

RTL and TLM both preserve functional data values. RTL additionally preserves signal transitions, sub-cycle delays, and arbitration detail — none of which survive in standard TLM-LT models.

---

**Q3. A team needs to boot Linux on a virtual platform model six months before RTL is ready. Which model type should they choose?**

- [ ] Gate-level netlist with SDF back-annotation
- [ ] RTL SystemVerilog simulation at full chip level
- [x] TLM Loosely Timed SystemC virtual platform
- [ ] SPICE transistor-level model of the CPU

TLM-LT virtual platforms run at speeds practical for OS boot (minutes per simulated second of activity). Gate-level or RTL simulation of a full SoC would require months of wall-clock time for a single Linux boot.

---

**Q4. In a SystemC TLM-2.0 model, what is the purpose of the quantum keeper (`tlm_quantumkeeper`)?**

- [ ] It prevents the simulation from using more than a fixed amount of RAM
- [ ] It enforces that all transactions complete within one clock cycle
- [x] It batches local time advances so processes avoid synchronizing with global simulation time on every transaction
- [ ] It limits the maximum burst length of a TLM generic payload

The quantum keeper lets an initiator accumulate local time over many transactions and only sync with global simulation time at quantum boundaries. This reduces context switches and dramatically improves simulation throughput.

---

**Q5. Which model abstraction level is the MINIMUM required to perform Static Timing Analysis (STA) and verify setup/hold times?**

- [ ] TLM Approximately Timed
- [ ] RTL register-transfer level
- [ ] Cycle-accurate micro-architectural model
- [x] Gate-level netlist with SDF back-annotated delays

STA requires propagation delays derived from actual logic gates and routing. RTL models logic functions but not propagation delays. Only a gate-level netlist with Standard Delay Format (SDF) files provides the information STA tools need.

---

**Q6. A TLM initiator calls `b_transport()` and passes `SC_ZERO_TIME` as the delay for every transaction. What is the most significant consequence?**

- [ ] The simulation will deadlock because the scheduler has no events to process
- [ ] The `tlm_generic_payload` data will be silently corrupted
- [x] The model cannot be used for performance analysis because all latency information is discarded
- [ ] The simulation will crash with a TLM protocol error

Zero-delay models are functionally valid and simulate very fast. The consequence is that all latency information is lost, making throughput and bandwidth analysis meaningless. Software bring-up can still be done, but performance studies require realistic delay annotations.
