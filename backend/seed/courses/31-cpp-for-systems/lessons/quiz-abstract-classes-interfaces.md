# Quiz: Abstract Classes and Interfaces

Test your understanding of pure virtual functions, abstract classes, interface design, and the NVI idiom.

---

**Q1. What makes a C++ class abstract?**

- [ ] It inherits from another class
- [x] It contains at least one pure virtual function
- [ ] It has a private constructor
- [ ] All its methods are `const`

_A class becomes abstract the moment it declares at least one pure virtual function (`= 0`). Having a private constructor makes a class non-instantiable by external code but does not make it abstract in the C++ language sense._

---

**Q2. What is the result of deleting a derived object through a base-class pointer when the base destructor is NOT virtual?**

- [ ] A compile-time error
- [ ] The derived destructor is called first, then the base destructor
- [x] Undefined behaviour — the derived destructor may never run, causing resource leaks
- [ ] The runtime automatically detects the type and calls the correct destructor

_Without a virtual destructor, `delete base_ptr` invokes only `Base::~Base()` via the static type. The derived destructor is skipped, which is undefined behaviour and typically causes resource leaks. Always declare `virtual ~Base()` in any polymorphic base class._

---

**Q3. Which statement about pure virtual functions with a body is correct?**

- [ ] Pure virtual functions cannot have a body — the `= 0` syntax forbids it
- [ ] A pure virtual function body must be defined inline inside the class
- [x] A pure virtual function can have an out-of-class body that derived classes may call via `Base::f()`
- [ ] Defining a body for a pure virtual function makes the class concrete

_`= 0` makes the class abstract and requires derived classes to override the function, but an out-of-class definition is allowed. The class stays abstract regardless. A pure virtual destructor in particular MUST have a body because destructors are always chained._

---

**Q4. In the Non-Virtual Interface (NVI) idiom, what is the role of the private virtual function?**

- [ ] It is the stable public API that callers invoke directly
- [ ] It prevents derived classes from overriding any behaviour
- [x] It is the customization point that derived classes override, called internally by the public non-virtual wrapper
- [ ] It replaces the constructor to initialize derived state

_NVI separates concerns: the public non-virtual method owns invariants, logging, and locking, while the private virtual hook is what derived classes specialize. Callers always go through the wrapper, so base-class pre/post-conditions cannot be bypassed._

---

**Q5. Which scenario is BEST served by runtime polymorphism (virtual functions) rather than templates?**

- [ ] A sort comparator used in a hot inner loop processing 500 million records
- [ ] A zero-overhead ring buffer in embedded firmware with a fixed element type
- [x] A plugin system where new driver implementations are loaded from shared libraries at runtime
- [ ] A compile-time-configured hash map where the key type is always known

_Virtual functions allow new concrete types to be introduced at runtime (via `dlopen` / `LoadLibrary`) without recompiling the host. Templates require all types to be known at compile time, making them unsuitable for plugins loaded dynamically._

---

**Q6. You want a class to be abstract but it has no natural pure virtual functions to declare. What is the recommended technique?**

- [ ] Make the constructor `protected`
- [ ] Declare all methods as `= delete`
- [x] Declare a pure virtual destructor with an out-of-class body
- [ ] Add a private data member with no accessors

_A pure virtual destructor (`virtual ~Base() = 0;` with an out-of-class `Base::~Base() {}`) is the idiomatic way to make a class abstract without forcing any particular method to be overridden. Every derived destructor implicitly calls the base destructor, so the body is mandatory._
