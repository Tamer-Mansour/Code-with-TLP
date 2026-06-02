# Quiz: Interrupts, Timers, and DMA

Test your understanding of interrupt modeling, virtual timers, DMA engines, priorities, and trigger types in SystemC virtual prototypes.

---

**Q1. In a SystemC VP, how is a peripheral interrupt line most commonly represented?**

- [ ] A TLM generic payload with a special interrupt command code
- [x] An `sc_signal<bool>` driven by the peripheral and read by the interrupt controller
- [ ] A shared global variable polled by the CPU model every 10 ns
- [ ] A C++ callback function registered at elaboration time

The standard approach is an `sc_signal<bool>` because it integrates naturally with SystemC's event-driven scheduler and is visible in waveform dumps.

---

**Q2. A virtual timer fires an interrupt every 1 ms of simulation time. Which SystemC mechanism ensures this timing is driven by simulation time rather than host wall-clock time?**

- [ ] `usleep(1000)` called inside the timer's SC_THREAD
- [ ] A C++ `std::chrono` high-resolution timer
- [x] `wait(1, SC_MS)` called inside the timer's SC_THREAD
- [ ] An `sc_clock` whose period is set to 1 ms of wall-clock time

`wait(1, SC_MS)` advances the SystemC simulation clock by exactly 1 ms, regardless of how long the host takes to execute that wait.

---

**Q3. A DMA engine model in a VP needs to read from a source address and write to a destination address in memory. Which socket arrangement is correct?**

- [ ] One TLM target socket only — the CPU master drives all transfers
- [ ] Two TLM target sockets — one for reads and one for writes
- [ ] One TLM initiator socket only — the DMA never receives MMIO writes
- [x] One TLM target socket (for CPU config) and one TLM initiator socket (for memory transfers)

The DMA must be both a slave (to receive register writes from the CPU) and a bus master (to issue its own memory read/write transactions).

---

**Q4. In a PLIC-based RISC-V system, which condition causes the PLIC to assert its interrupt line to the CPU?**

- [ ] Any source has a non-zero priority, regardless of threshold or enable bits
- [ ] The number of pending interrupts exceeds a watermark register
- [x] At least one enabled, pending source has a priority strictly greater than the hart's threshold register
- [ ] All enabled sources have been claimed and not yet completed

The PLIC specification requires that a source be enabled for the hart, pending, and have a priority strictly greater than the hart's priority threshold before the external interrupt line is asserted.

---

**Q5. An ISR for a level-triggered UART interrupt returns without reading any data from the UART FIFO. What happens next?**

- [ ] The interrupt line de-asserts automatically when the ISR executes MRET
- [ ] The interrupt is silently discarded by the interrupt controller
- [x] The interrupt fires again immediately because the UART line is still asserted
- [ ] The CPU locks up waiting for the interrupt to clear

Level-triggered interrupts remain asserted while the condition is true. If the ISR does not clear the source (drain the FIFO / clear the status register), the peripheral line stays high and the interrupt fires again the instant the ISR returns.

---

**Q6. Which statement correctly describes the difference between edge-triggered and level-triggered interrupts in a VP context?**

- [ ] Edge-triggered interrupts require the interrupt controller to hold the line high; level-triggered interrupts use a pulse
- [ ] Both types behave identically in simulation because SystemC delta cycles make edge detection redundant
- [ ] Level-triggered interrupts can only be used with timer peripherals; edge-triggered with FIFOs
- [x] Edge-triggered interrupts latch on a signal transition and can be missed if interrupts are disabled at that moment; level-triggered interrupts persist until software clears the source

Edge detection latches a transient event; if the edge occurs while the CPU has interrupts disabled, the latch may not be processed until the interrupt controller is re-enabled — but if the pulse is gone by then and the latch is not set, the event is lost.
