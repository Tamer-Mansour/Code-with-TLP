# Quiz: The SystemC Simulation Kernel

**Q1. What does the SystemC kernel do when the event queue is empty at the current simulation time?**

- [ ] It raises a simulation error and aborts.
- [ ] It spins in a busy loop waiting for external input.
- [x] It advances simulation time to the next scheduled event.
- [ ] It executes all SC_METHOD processes one more time.

The kernel only advances simulation time when all delta-cycle activity at the current time is exhausted. The next event time is taken from the global timed event queue.

---

**Q2. A process calls `sig.write(42)` and then immediately calls `sig.read()`. What value does `read()` return?**

- [x] The old value of `sig`, before the write.
- [ ] 42, because the write takes effect immediately.
- [ ] An undefined/garbage value.
- [ ] 0, because the signal is reset on write.

Signal writes are deferred to the update phase. Within the same evaluate phase, `read()` always returns the pre-update value.

---

**Q3. Which notification mode fires an event in the SAME delta cycle's evaluate phase?**

- [ ] `my_event.notify(SC_ZERO_TIME)`
- [x] `my_event.notify()`
- [ ] `my_event.notify(1, SC_NS)`
- [ ] `my_event.notify(SC_ZERO_TIME + SC_ZERO_TIME)`

`notify()` with no argument is an immediate notification. It activates waiting processes within the same evaluate phase. `notify(SC_ZERO_TIME)` schedules a delta notification — the event fires after the current update phase, in the next delta's evaluate.

---

**Q4. What is the time resolution in SystemC and what does it affect?**

- [ ] The period of the fastest clock in the design.
- [ ] The granularity of wall-clock measurements during simulation.
- [x] The smallest representable time quantum; `sc_time` values are rounded to multiples of it.
- [ ] The maximum simulation time before overflow.

Time resolution is set with `sc_set_time_resolution()` and determines the tick size for the internal 64-bit time counter. All `sc_time` values are stored as integer multiples of this resolution.

---

**Q5. How many delta cycles occur at a given simulation timestamp?**

- [ ] Exactly one — evaluate and update happen once per time step.
- [ ] A fixed number set by the designer.
- [x] As many as needed until no signal changes in the update phase (quiescence).
- [ ] Always zero — delta cycles only occur during initialization.

Delta cycles repeat (evaluate → update → check for new triggers) until the update phase produces no new signal notifications. This is called quiescence. Only then does simulation time advance.

---

**Q6. An `SC_METHOD` process is triggered repeatedly between simulation time 10 ns and 11 ns without time advancing. What is the most likely cause?**

- [ ] The process is waiting on a timed event.
- [ ] A `sc_clock` is driving it with a 1 ns period.
- [x] Two signals or events are notifying each other with `SC_ZERO_TIME`, creating an infinite delta loop.
- [ ] The process called `sc_stop()` inside its body.

Mutual `SC_ZERO_TIME` notifications between processes create an infinite chain of delta cycles at the same simulation time. Simulation time never advances. This is a common bug in models with circular combinational dependencies.
