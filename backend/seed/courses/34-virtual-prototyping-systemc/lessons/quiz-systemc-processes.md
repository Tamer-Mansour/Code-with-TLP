# Quiz: SystemC Processes

Test your understanding of `SC_METHOD`, `SC_THREAD`, `SC_CTHREAD`, `wait()`, and `next_trigger()`.

---

**Q1. Which statement correctly describes SC_METHOD?**

- [ ] It can call `wait()` to suspend execution until the next clock edge.
- [x] It runs its function body to completion every time its sensitivity list fires.
- [ ] It preserves its call stack between activations.
- [ ] It must always be paired with `reset_signal_is()`.

_SC_METHOD is a run-to-completion process; it cannot call `wait()` and does not save a stack between runs._

---

**Q2. An SC_THREAD body contains `while(true) { do_work(); }` with no `wait()` call inside the loop. What happens?**

- [ ] The loop runs correctly and advances simulation time on each iteration.
- [ ] The compiler refuses to build the module.
- [x] The simulation hangs because the thread never yields control to the kernel.
- [ ] The thread terminates after the first pass through the loop.

_Without `wait()`, the thread never suspends; the SystemC scheduler never gets CPU time back, so simulated time never advances and the program freezes._

---

**Q3. Which sensitivity registration fires the process on the RISING EDGE only?**

- [ ] `sensitive << clk;`
- [ ] `sensitive << clk.negedge_event();`
- [x] `sensitive << clk.pos();`
- [ ] `sensitive << clk.value_changed_event();`

_`clk.pos()` adds the positive-edge event. Plain `sensitive << clk` fires on both edges; `value_changed_event()` is equivalent to the plain form._

---

**Q4. What is the purpose of next_trigger() inside an SC_METHOD?**

- [ ] It suspends the method until the specified event fires.
- [ ] It restarts the method from the beginning immediately.
- [x] It overrides the static sensitivity list for exactly one subsequent activation.
- [ ] It converts the method into an SC_THREAD dynamically.

_`next_trigger()` sets the trigger condition for the next (and only the next) activation of the method, after which static sensitivity resumes._

---

**Q5. In SC_CTHREAD, which forms of wait() are legal?**

- [ ] `wait(some_signal.value_changed_event());`
- [ ] `wait(50, SC_NS);`
- [x] `wait()` and `wait(N)` where N is an integer count of clock edges.
- [ ] All the same forms as SC_THREAD.

_SC_CTHREAD is bound to a single clock edge. Only `wait()` (next edge) and `wait(N)` (N edges) are legal; time-based or event-based waits are not permitted._

---

**Q6. A module registers SC_METHOD(compute) but omits signal `c` from the sensitivity list, even though `compute` reads `a`, `b`, and `c`. What is the most likely consequence?**

- [ ] A compile-time error listing the missing signal.
- [ ] A simulation runtime error when `c` changes value.
- [ ] The method fires correctly because SystemC auto-detects all reads.
- [x] A simulation/synthesis mismatch: simulation ignores changes to `c`, but synthesised hardware responds to them.

_SystemC does not auto-detect signal reads. Missing a signal from the sensitivity list is silent in simulation but creates a functional discrepancy with the synthesised gate-level netlist._
