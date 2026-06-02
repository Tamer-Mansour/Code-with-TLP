# The VP/OS Interview Question Bank

This lesson collects the most frequently asked Virtual Prototyping, SystemC/TLM, and embedded OS interview questions, grouped by category. For each question, a crisp answer is provided — the kind you can deliver in 60–90 seconds.

## Category 1: Fundamentals

**Q: What is a Virtual Prototype and why do SoC teams build one?**

> A VP is a software model of an SoC that is functionally equivalent to the hardware but runs on a host workstation. Teams build VPs to enable software development 12–18 months before first silicon, to explore architecture trade-offs, and to create a reference model for DV scoreboards.

**Q: What is the difference between a functional model, an approximately-timed model, and a cycle-accurate model?**

> Functional: correct output, no time. Approximately-timed: adds coarse timing (±10–30 %), fast simulation. Cycle-accurate: exact microarchitectural state at every clock edge, 10–100× slower than AT but far faster than RTL.

**Q: What is TLM-2.0 and what problem does it solve?**

> TLM-2.0 is an Accellera standard for transaction-level communication in SystemC. It defines a generic payload (address, data, command, response), a blocking transport interface (`b_transport`), and a non-blocking interface (`nb_transport`). It solves the lack of interoperability between vendor models: any TLM-2.0 compliant initiator can connect to any TLM-2.0 compliant target without custom glue.

---

## Category 2: SystemC Mechanics

**Q: What is the difference between `SC_THREAD` and `SC_METHOD`?**

> `SC_METHOD` is a process that runs to completion on every trigger — no suspension allowed. `SC_THREAD` can call `wait()` to suspend and resume, making it natural for sequential protocols. Threads have a stack; methods do not.

**Q: What happens if you call `wait()` inside an `SC_METHOD`?**

> It causes a fatal simulation error at runtime. Methods are not allowed to block.

**Q: Explain `sc_time` resolution and why it matters.**

> SystemC tracks simulation time as a 64-bit integer of time units at a fixed resolution (e.g., 1 ps). If you try to represent 0.3 ns at 1 ps resolution, you get 300 units — exact. If you use 1 ns resolution, 0.3 ns rounds to 0 ns silently, causing invisible timing errors. Set resolution with `sc_set_time_resolution()` before any time object is created.

**Q: What is a temporal decoupling quantum and when would you increase it?**

> The quantum is the maximum amount of simulated time an initiator can run ahead of the global simulation time before synchronizing with the scheduler. Larger quanta (e.g., 100 µs) reduce context switches and increase speed but reduce timing accuracy. Increase it when simulation speed is the bottleneck and timing accuracy of ±100 µs or worse is acceptable.

---

## Category 3: TLM Protocol

**Q: What is the difference between `b_transport` and `nb_transport`?**

> `b_transport` is blocking: the caller suspends until the transport completes. `nb_transport` is non-blocking: the caller sends a payload and returns immediately; the response arrives via a separate backward path. AT models use `nb_transport`; LT models use `b_transport`.

**Q: What are the four TLM-2.0 response status values?**

> `TLM_OK_RESPONSE`, `TLM_INCOMPLETE_RESPONSE`, `TLM_GENERIC_ERROR_RESPONSE`, `TLM_ADDRESS_ERROR_RESPONSE`. Targets must set one of these before returning from `b_transport`.

**Q: What is a DMI (Direct Memory Interface) and when is it used?**

> DMI allows an initiator to obtain a raw pointer to a target's memory region, bypassing the TLM socket for subsequent accesses. Used for high-speed bulk data transfer (e.g., DMA fills) where `b_transport` overhead would be prohibitive. The target must invalidate the DMI hint when its memory is remapped.

---

## Category 4: VP vs. RTL vs. Hardware

**Q: Can a VP replace RTL simulation for DV sign-off?**

> No. RTL simulation with SVA assertions, constrained-random stimulus, and coverage closure is required for DV sign-off. A VP has no X-state, no formal proof capability, no signal-level assertions, and no gate-level timing. It can accelerate DV by serving as the reference model in a scoreboard.

**Q: What is the primary reason to build a VP before RTL is available?**

> Software head-start: firmware, OS, and driver development can begin 12–18 months before first silicon, dramatically compressing time-to-market.

**Q: Name three things an FPGA prototype can do that a VP cannot.**

> 1. Run at real-time speed (MHz range). 2. Interface with real physical peripherals (UART, I2C, DDR). 3. Exercise board-level hardware integration.

---

## Category 5: Embedded OS and Driver Questions

**Q: What is the difference between a uniprocessor RTOS and an SMP Linux kernel in the context of a VP?**

> A uniprocessor RTOS runs one task at a time; the VP only needs one simulated CPU core, making scheduling deterministic. SMP Linux may schedule tasks across multiple cores; the VP needs multiple simulated CPU models and a cache coherence model, increasing VP complexity significantly.

**Q: How do you model interrupt delivery in a SystemC VP?**

> An interrupt line is modeled as an `sc_signal<bool>`. The peripheral asserts the signal; the CPU model's interrupt controller monitors it via a sensitive method or thread, then invokes the interrupt handler in the simulated software environment.

**Q: What is MMIO and how is it modeled in TLM?**

> Memory-Mapped I/O maps peripheral registers into the CPU address space. In TLM, an initiator performs `b_transport` writes/reads to the peripheral's base address. The interconnect (router) decodes the address and forwards the transaction to the correct target socket. The target's `b_transport` implementation updates the register model and may trigger side effects (e.g., asserting an interrupt).

---

## Category 6: Debugging and Methodology

**Q: How do you debug a driver that works on the VP but fails on silicon?**

> Step 1: Check whether the VP register model matches the RTL spec exactly (common source of divergence). Step 2: Check timing assumptions — the VP may deliver a status flag immediately; RTL may take N cycles. Step 3: Check X-state issues by inspecting the RTL simulation log. Step 4: Add waveform tracing to the RTL simulation and compare transaction logs with the VP.

**Q: What is the role of a VP in post-silicon debug?**

> When silicon behaves unexpectedly, the VP provides a known-good software execution reference. Engineers run the same sequence on the VP to determine whether the bug is in software (reproducible on VP) or hardware (not reproducible on VP).
