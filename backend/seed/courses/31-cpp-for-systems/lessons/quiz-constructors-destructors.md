# Quiz: Constructors and Destructors

Test your understanding of object construction, destruction, initialization order, and the lifetime rules covered in this module.

---

**Q1. A class declares one constructor: `Widget(int id)`. Which statement is true?**

- [ ] The compiler still generates a default constructor `Widget()`.
- [x] The compiler does NOT generate a default constructor because a user-declared constructor exists.
- [ ] The compiler generates both a default constructor and a copy constructor.
- [ ] The code is ill-formed; every class must explicitly declare a default constructor.

*Explanation: Once you declare any constructor, the implicit default constructor is suppressed. You must write `Widget() = default;` or define it explicitly to restore it.*

---

**Q2. Given the class below, in what order are the members initialized when `Obj o(5, 10)` is called?**

```cpp
class Obj {
    int b;
    int a;
public:
    Obj(int x, int y) : a(x), b(y) {}
};
```

- [ ] `a` first, then `b` — because `a` appears first in the initializer list.
- [ ] `a` first, then `b` — because `x` is the first parameter.
- [x] `b` first, then `a` — because members are initialized in declaration order, not initializer-list order.
- [ ] The order is unspecified by the standard.

*Explanation: The C++ standard mandates that non-static data members are initialized in the order they are declared in the class, regardless of the order in which they appear in the member initializer list. Here `b` is declared before `a`.*

---

**Q3. What does marking a constructor `explicit` prevent?**

- [ ] The constructor from being called at all outside the class.
- [ ] The constructor from being inherited by derived classes.
- [x] The constructor from being used as an implicit conversion by the compiler.
- [ ] The constructor from accepting more than one argument.

*Explanation: `explicit` disables the use of a constructor (or conversion operator) as an implicit conversion sequence. It has no effect on direct initialization syntax like `T obj(value)` or `T obj{value}`.*

---

**Q4. Which of the following correctly describes delegating constructors (C++11)?**

- [ ] A delegating constructor calls a base-class constructor in its member initializer list.
- [x] A delegating constructor calls another constructor of the **same** class in its member initializer list, and the delegating constructor's body runs after the target constructor completes.
- [ ] A delegating constructor can list both the delegation and other member initializers in the same initializer list.
- [ ] A delegating constructor's body runs before the target constructor's body.

*Explanation: Delegation targets must be constructors of the same class. When delegation is specified, no other member initializers may appear in that constructor's initializer list. The target constructor runs entirely (body included) before the delegating constructor's body.*

---

**Q5. A base class has a non-virtual destructor and an object is deleted through a base-class pointer pointing to a derived object. What happens?**

- [ ] The derived destructor runs first, then the base destructor — correct behavior.
- [ ] The program always crashes with a segfault.
- [x] The behavior is undefined; the derived destructor may not be called, potentially leaking resources.
- [ ] The compiler refuses to compile `delete base_ptr` when the destructor is non-virtual.

*Explanation: Deleting a derived object through a base pointer when the base destructor is non-virtual is undefined behavior per the C++ standard. In practice, only the base destructor runs on most compilers, leaking any resources owned exclusively by the derived part. Always declare base-class destructors `virtual`.*

---

**Q6. Given a class hierarchy `A → B → C` (A is base, C is most derived), when a `C` object is destroyed, what is the correct destruction order?**

- [ ] A destructor, then B destructor, then C destructor.
- [ ] C destructor body, then A destructor, then B destructor.
- [x] C destructor body, then B destructor body, then A destructor body — most-derived to most-base.
- [ ] All three destructors run in an unspecified order.

*Explanation: Destruction is the exact reverse of construction. Construction goes A → B → C; destruction goes C → B → A. Within each destructor, the body runs first, then members are destroyed in reverse declaration order, then the base class destructor is invoked.*
