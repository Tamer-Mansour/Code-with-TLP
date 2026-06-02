# Quiz: SystemC Modules and Structure

Test your understanding of `sc_module`, constructors, hierarchy, ports, and composition in SystemC.

---

**Q1. What does the `SC_CTOR(MyModule)` macro expand to?**

- [ ] `MyModule() : sc_module() {}`
- [x] `MyModule(sc_module_name name_) : sc_module(name_) {}`
- [ ] `MyModule(const char* name_) : sc_module() {}`
- [ ] `MyModule(std::string name_) : sc_module(name_.c_str()) {}`

`SC_CTOR` generates a constructor that accepts `sc_module_name` and forwards it to the `sc_module` base class, which registers the instance in the kernel's object hierarchy. A plain `const char*` would bypass the kernel's name-stack mechanism.

---

**Q2. At what point in the simulation lifecycle is it legal to bind ports to signals?**

- [ ] Inside an `SC_THREAD` process after `wait()` returns
- [ ] Inside `start_of_simulation()`
- [x] During elaboration — in the module constructor or `before_end_of_elaboration()`
- [ ] Anywhere before `sc_stop()` is called

Port binding is an elaboration-time operation. The kernel validates all bindings at the end of elaboration; binding after `sc_start()` is illegal and results in undefined behavior or a kernel error.

---

**Q3. Which callback should you use to open a VCD trace file and register signals with `sc_trace()`?**

- [ ] `before_end_of_elaboration()` — before any validation
- [ ] `start_of_simulation()` — just before the first delta cycle
- [x] `end_of_elaboration()` — after port binding validation is complete
- [ ] Inside the module constructor

`end_of_elaboration` fires after all ports have been validated as bound. At this point all signals exist and are safely accessible. Opening the trace file here avoids registering signals that might still be unbound during `before_end_of_elaboration`.

---

**Q4. You have two processes in the same module that both write to a plain `int` member variable. What is the safest fix?**

- [ ] Declare both processes with `dont_initialize()`
- [ ] Use `SC_CTHREAD` instead of `SC_METHOD`
- [x] Change the shared variable to `sc_signal<int>` so writes are queued and readers are notified correctly
- [ ] Use `volatile int` to ensure visibility

When multiple processes share state, `sc_signal<T>` provides the correct semantics: writes are queued to the update phase, preventing write-write conflicts within a delta cycle and properly triggering sensitivity-list notifications for any readers.

---

**Q5. Which statement about `sc_in<T>` ports is correct?**

- [x] `sc_in<T>` is a reference to an external channel; it stores no value itself
- [ ] `sc_in<T>` holds its own copy of the value, like a local variable
- [ ] `sc_in<T>` can be read before it is bound to a signal
- [ ] `sc_in<T>` and `sc_signal<T>` are interchangeable anywhere in the design

A port is a proxy object. `read()` on an unbound `sc_in<T>` dereferences a null internal pointer, causing undefined behavior. Ports carry no value storage — they delegate to the channel they are bound to.

---

**Q6. You need 8 identical DMA channel modules connected to 8 separate `sc_signal<bool>` done lines. What is the correct approach?**

- [ ] Declare 8 separate module members: `Dma dma0, dma1, ..., dma7`
- [ ] Declare one module and call its constructor 8 times in the parent constructor body
- [x] Use `std::vector<Dma*>` and `std::vector<sc_signal<bool>*>`, constructing each with a unique generated name in a loop
- [ ] Use a single `Dma` module and multiplex the done signal with an index register

For parameterized arrays, heap allocation with a vector is the standard SystemC idiom. Each instance must receive a unique name string. Declaring 8 members by hand does not scale and must be redone for every different value of N.
