# Quiz: Encapsulation and Abstraction

Test your understanding of encapsulation, abstraction, class invariants, the Pimpl idiom, and API design.

---

**Q1. Which of the following BEST describes the difference between encapsulation and abstraction?**

- [ ] Encapsulation is about using `private` keywords; abstraction means using templates.
- [x] Encapsulation protects data by controlling access; abstraction hides complexity by exposing only the relevant interface for a given level.
- [ ] They are synonyms for the same concept in OOP.
- [ ] Abstraction applies only to virtual functions; encapsulation applies to data members.

*Explanation: Encapsulation is the mechanism (access specifiers, invariant enforcement); abstraction is the design goal of operating at the right conceptual level. They cooperate but answer different questions.*

---

**Q2. A class has `double balance_` as a private member and returns `double& get_balance()` (a non-const reference). What is the problem?**

- [ ] Returning a reference is always undefined behaviour.
- [ ] The function should return `const double&` instead of `double&`.
- [x] Returning a mutable reference to a private member defeats encapsulation — callers can set any value, bypassing invariant checks.
- [ ] There is no problem; this is standard practice for performance.

*Explanation: A non-const reference to a private field lets any caller write arbitrary values, completely bypassing setters and invariant enforcement. Return by value or `const` reference instead.*

---

**Q3. What is the PRIMARY benefit of the Pimpl idiom?**

- [ ] It makes objects cheaper to copy because all data is behind a pointer.
- [ ] It allows inheritance without virtual dispatch.
- [x] It creates a compilation firewall: changes to private members do not force recompilation of translation units that include the header.
- [ ] It eliminates the need for a destructor.

*Explanation: Pimpl's defining benefit is that the header exposes only an opaque pointer, so adding or changing private members requires recompiling only the one `.cpp` that defines `Impl`, not every consumer of the header.*

---

**Q4. Which statement about class invariants is CORRECT?**

- [ ] Invariants are checked by the compiler at every public method call automatically.
- [ ] An invariant only needs to hold after construction, not after subsequent method calls.
- [x] A class invariant must hold before and after every public method call; the constructor is responsible for establishing it initially.
- [ ] Invariants apply only to `const` member functions.

*Explanation: A class invariant is a persistent condition. The constructor establishes it; every mutating public method must leave the object satisfying it. `assert` and debug checks help verify this at runtime.*

---

**Q5. In the context of a Platform Abstraction Layer (PAL) for embedded systems, what does "information hiding" achieve?**

- [ ] It prevents the hardware from being accessed at runtime.
- [ ] It makes the code slower because of extra function call overhead.
- [x] It confines hardware-specific register addresses and vendor headers to one location, allowing the rest of the codebase to remain platform-independent.
- [ ] It is only useful when using C++; C code cannot benefit from information hiding.

*Explanation: A PAL exposes generic functions (`gpio_set_high`) and hides all vendor-specific register writes inside a single directory. Porting to new hardware means rewriting only the PAL, not the application logic.*

---

**Q6. Which C++ technique provides compile-time polymorphism with zero virtual dispatch overhead?**

- [ ] `std::function` callbacks
- [ ] Pure virtual base classes
- [ ] `dynamic_cast` at call sites
- [x] CRTP (Curiously Recurring Template Pattern)

*Explanation: CRTP uses templates so derived-class methods are resolved at compile time via `static_cast`, producing direct calls the compiler can inline — no vtable, no indirect branch.*
