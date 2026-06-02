# Quiz: Introduction to Virtual Prototypes

Test your understanding of the core concepts from this module. Each question has exactly one correct answer.

---

**Q1. What is the primary purpose of a virtual prototype in chip development?**

- [ ] To replace RTL simulation for hardware verification
- [ ] To generate GDSII layout files automatically
- [x] To enable software development before physical hardware is available
- [ ] To model analog signal behavior with SPICE accuracy

*A VP is a software model of a hardware system that allows firmware, drivers, and OS software to be developed and validated before silicon is fabricated. It does not replace RTL verification or analog simulation.*

---

**Q2. Which abstraction level does TLM-2.0 target in SystemC virtual prototypes?**

- [ ] Gate level — every logic gate is modeled
- [ ] RTL level — every clock edge and flip-flop is modeled
- [x] Transaction level — communication is modeled as high-level read/write transactions
- [ ] Layout level — physical placement and routing is modeled

*TLM-2.0 (Transaction-Level Modeling) models bus communication as discrete transactions (read/write payloads) rather than individual signal transitions. This abstraction gives 100x–10,000x speedup over RTL simulation.*

---

**Q3. Which of the following is a key limitation of virtual prototypes?**

- [ ] They require a physical chip to be fabricated before they can run
- [ ] They can only model a single peripheral at a time
- [ ] They are too slow to run operating systems like Linux
- [x] They cannot accurately model analog behavior such as PLL lock time or ADC noise

*VPs model digital register interfaces of analog components but cannot simulate electrical analog behavior. PLLs, ADCs, and RF circuits must be validated on real hardware or in SPICE-class simulators.*

---

**Q4. What does "shifting software left" mean in the context of virtual prototypes?**

- [ ] Moving the software team to a different office location
- [ ] Replacing hardware engineers with software engineers
- [x] Starting software development earlier in the project timeline by using a VP instead of waiting for silicon
- [ ] Reducing the number of software features to simplify the product

*"Shift left" means moving activities earlier on the project timeline (to the left on a Gantt chart). VPs enable software to start 12–18 months earlier by providing an executable hardware model before silicon exists.*

---

**Q5. When comparing a virtual prototype to FPGA-based emulation, which statement is most accurate?**

- [ ] FPGA emulation is cheaper and easier to set up than a VP
- [x] A VP is available much earlier and is more cost-effective, but FPGA emulation runs closer to real hardware speed
- [ ] VPs run faster than FPGA emulation and are equally accurate
- [ ] FPGA emulation can model analog behavior while VPs cannot

*FPGA emulation requires completed RTL and expensive hardware platforms ($1M+), but runs near real-time. VPs can be built at architecture phase on a workstation, but run 10x–1000x slower than real silicon. Each has a distinct role.*

---

**Q6. Which industry use case best illustrates the value of fault injection on a virtual prototype?**

- [ ] Measuring DDR4 memory training latency on a new SoC
- [ ] Rendering a 3D game to benchmark GPU performance
- [x] Validating automotive firmware error handlers under ISO 26262 by injecting bus errors and watchdog timeouts
- [ ] Calibrating ADC offset error across temperature on a mixed-signal chip

*Automotive safety standards (ISO 26262) require that diagnostic software correctly handles fault conditions. VPs allow bus errors, CRC failures, and watchdog timeouts to be injected safely and repeatably — conditions that would risk destroying real ECU hardware.*
