# Quiz: Sensitivity, Events, and Channels

**Q1. What happens when `sc_signal<int>::write(42)` is called and the signal already holds the value 42?**

- [ ] The signal notifies all sensitive processes immediately.
- [ ] The signal schedules an update for the next delta cycle, which triggers a notification.
- [x] No notification is generated; sensitive processes are not awakened.
- [ ] A runtime error is thrown because the value is unchanged.

_`sc_signal` only notifies when the committed value changes; writing the same value is a no-op with respect to notifications._

---

**Q2. Which statement correctly describes the difference between `notify()` and `notify(SC_ZERO_TIME)`?**

- [ ] Both wake sensitive processes in the same delta cycle.
- [x] `notify()` wakes processes in the current evaluation phase; `notify(SC_ZERO_TIME)` wakes them at the start of the next delta cycle.
- [ ] `notify(SC_ZERO_TIME)` advances simulation time by one nanosecond before waking processes.
- [ ] There is no difference; both are aliases for immediate notification.

_Immediate `notify()` inserts processes into the current runnable set, while delta notification defers until the next evaluation phase after channel updates._

---

**Q3. An SC_MODULE declares `SC_METHOD(foo); sensitive << a << b << c;`. Which of the following is true?**

- [ ] `foo()` runs only when all three signals change simultaneously.
- [x] `foo()` runs whenever any one of `a`, `b`, or `c` changes value.
- [ ] `foo()` can call `wait()` to block until all three signals change.
- [ ] The sensitivity list is re-evaluated every time `foo()` runs.

_Static sensitivity is an OR list; the method wakes on any single event in the list, and `SC_METHOD` processes cannot call `wait()`._

---

**Q4. Which channel type supports containing internal `SC_THREAD` processes?**

- [ ] `sc_prim_channel`
- [ ] `sc_signal<T>`
- [ ] `sc_fifo<T>`
- [x] `sc_channel` (hierarchical channel)

_Hierarchical channels inherit from `sc_module` and can therefore declare and use `SC_THREAD`, `SC_METHOD`, submodules, and ports — features unavailable in primitive channels._

---

**Q5. A thread calls `wait(5, SC_NS, ready_event)`. The `ready_event` fires after 3 ns. What happens?**

- [ ] The thread waits the full 5 ns and ignores the event.
- [ ] The thread throws a simulation exception because mixed waits are unsupported.
- [x] The thread wakes at T+3 ns when the event fires, before the timeout expires.
- [ ] The thread wakes at T+5 ns and `ready_event` is discarded.

_The two-argument wait form is a "whichever comes first" timeout: if the event fires before the timeout, the process wakes immediately at the event time._

---

**Q6. What is the purpose of `request_update()` in a primitive channel?**

- [ ] It immediately commits a written value so that `read()` returns the new value in the same delta.
- [ ] It requests that the simulation kernel restart from time zero.
- [ ] It registers the channel with the VCD tracer for waveform output.
- [x] It tells the kernel to call the channel's `update()` method at the end of the current delta cycle, committing buffered writes.

_`request_update()` is the two-phase write handshake: write queues the new value and calls `request_update()`; the kernel calls `update()` after all processes have run, ensuring deterministic reads throughout the evaluation phase._
