# Quiz: C++ Essentials for SystemC

Test your understanding of the C++ features that underpin SystemC modeling.

---

**Q1. What is the primary reason SystemC uses C++ templates for port types such as `sc_in<T>` and `sc_out<T>`?**

- [ ] Templates allow port types to be resolved at runtime, enabling dynamic rebinding.
- [x] Templates enforce type safety at compile time, so connecting mismatched port types is a compilation error rather than a runtime failure.
- [ ] Templates reduce the binary size of the simulation executable by sharing a single implementation.
- [ ] Templates are required by the IEEE 1666 standard to support VHDL interoperability.

_Templates instantiate separate type-specific code at compile time. A `sc_in<int>` and `sc_in<double>` are distinct types, so the compiler rejects an attempt to bind one to the other immediately, before any simulation runs._

---

**Q2. Which of the following correctly describes the difference between a pointer and a reference in C++?**

- [ ] A pointer cannot be null, while a reference can be null.
- [ ] A reference stores the address of an object and must be explicitly dereferenced with `*`.
- [x] A reference is an alias that must be bound at declaration and cannot be rebound, while a pointer stores an address and can be null or reassigned.
- [ ] Both pointers and references are identical in behaviour; the choice is purely stylistic.

_A reference has no null state and no rebinding after initialisation. TLM transport functions pass `tlm_generic_payload` by reference precisely because it is always valid and modification of the caller's object is intended._

---

**Q3. What does `SC_CTOR(MyModule)` expand to, and why must the module name be forwarded to the base class?**

- [ ] It expands to a default constructor with no arguments; the name is optional in SystemC.
- [ ] It expands to `MyModule() : sc_object()` — `sc_module` does not need the name string.
- [x] It expands to `MyModule(sc_module_name nm) : sc_module(nm)` — the name string must reach `sc_module` so the simulator can build a named object hierarchy.
- [ ] It expands to `MyModule(const char* nm)` and stores the name only in the derived class.

_`sc_module` registers the module in the simulator's object tree using the name string. Failing to forward it causes the hierarchy to be unnamed or corrupted at elaboration time._

---

**Q4. Which statement about virtual destructors is correct in the context of SystemC?**

- [ ] Virtual destructors are unnecessary because `sc_module` uses reference counting for cleanup.
- [ ] Only leaf modules need a virtual destructor; top-level modules do not.
- [ ] Virtual destructors cause undefined behaviour when modules are deleted through a base-class pointer.
- [x] A base class that is deleted through a base-class pointer must have a virtual destructor; without it, only the base destructor runs and the derived class leaks resources.

_If `delete ptr` is called where `ptr` is of type `sc_module*` but points to a derived module, only `~sc_module()` runs unless the destructor chain is virtual. `sc_module` declares `virtual ~sc_module()` for exactly this reason._

---

**Q5. What is RAII, and how does it apply to sub-module creation in SystemC?**

- [ ] RAII means "Runtime Allocation Is Immediate" — modules are allocated by the kernel, not by user code.
- [x] RAII means "Resource Acquisition Is Initialisation" — by wrapping a heap-allocated sub-module in a `std::unique_ptr`, its destructor is guaranteed to run (and the module freed) when the containing object is destroyed, even if an exception occurs.
- [ ] RAII means modules must be declared as `static` locals so the compiler controls their lifetime.
- [ ] RAII is a VHDL concept adapted into C++/SystemC for process lifetime management.

_RAII ties resource lifetime to object lifetime. A `std::unique_ptr<Adder>` member in a parent module will call `delete` on the `Adder` when the parent is destroyed, with no explicit destructor needed in the parent._

---

**Q6. Which capture form in a C++ lambda risks undefined behaviour if the lambda outlives the enclosing scope?**

- [ ] `[=]` — capture by value
- [x] `[&]` — capture by reference
- [ ] `[]` — capture nothing
- [ ] `[this]` — capture the current object pointer

_Capturing a local variable by reference (`[&]`) means the lambda holds a reference into the enclosing stack frame. If the lambda is stored (e.g., in a `std::function` member) and called after the enclosing function returns, the reference is dangling and the behaviour is undefined._
