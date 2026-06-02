# Static Binding vs Dynamic Binding

**Binding** is the act of connecting a function call in source code to a specific function body. C++ performs this binding at two different stages depending on whether the function is virtual.

## Static Binding (Early Binding)

The compiler resolves the call at compile time using only the **static type** — the type declared in the source code. Non-virtual member functions, free functions, overloaded functions, and template instantiations all use static binding.

```cpp
struct Animal {
    void breathe() const { std::cout << "Animal breathes\n"; }  // non-virtual
};

struct Dog : Animal {
    void breathe() const { std::cout << "Dog breathes\n"; }     // hides, not overrides
};

Dog d;
Animal& a = d;
a.breathe();   // "Animal breathes" — static type is Animal, resolved at compile time
d.breathe();   // "Dog breathes"    — static type is Dog
```

The compiler emits a direct `CALL` instruction to the known function address. This enables:
- **Inlining** — the body can be substituted at the call site.
- **Constant folding** — if arguments are constant, the result may be computed at compile time.
- **Zero overhead** — no pointer indirection.

## Dynamic Binding (Late Binding)

When a function is declared `virtual` in the base class, the call through a base pointer or reference is resolved at **runtime** using the vtable. The static type of the pointer may differ from the dynamic type of the pointed-to object.

```cpp
struct Animal {
    virtual void speak() const { std::cout << "...\n"; }
    virtual ~Animal() = default;
};

struct Dog : Animal {
    void speak() const override { std::cout << "Woof\n"; }
};

struct Cat : Animal {
    void speak() const override { std::cout << "Meow\n"; }
};

Animal* a = new Dog();   // static type: Animal*  dynamic type: Dog
a->speak();              // "Woof" — resolved at runtime
delete a;

a = new Cat();
a->speak();              // "Meow" — resolved at runtime
delete a;
```

At the machine level the compiler generates roughly:

```asm
; a->speak() via vtable
mov rax, [rdi]          ; load vptr (first field of object)
call [rax + offset]     ; call through vtable slot
```

## Forcing Static Binding on a Virtual Function

You can suppress dynamic dispatch by qualifying the call with the class name:

```cpp
struct Base {
    virtual void run() { std::cout << "Base::run\n"; }
};

struct Derived : Base {
    void run() override { std::cout << "Derived::run\n"; }
    void example() {
        run();          // dynamic dispatch — calls Derived::run
        Base::run();    // static dispatch  — calls Base::run directly
    }
};
```

This is occasionally useful in performance-critical paths or when intentionally calling the base implementation.

## Practical Decision Table

| Scenario | Use |
|----------|-----|
| All types known at compile time | Static binding (templates, overloads) |
| Types vary, known set | Consider `std::variant` + `std::visit` (still static) |
| Open-ended extensibility, plugins | Dynamic binding (virtual) |
| Hot loop, latency-sensitive | Prefer static; profile before adding virtual |

## A Subtle Pitfall: Constructors Always Use Static Binding

Inside a constructor or destructor, all virtual function calls resolve statically to the currently-being-constructed class. The vtable for the derived class is not yet installed.

```cpp
struct Base {
    Base() { setup(); }
    virtual void setup() { std::cout << "Base::setup\n"; }
};
struct Derived : Base {
    void setup() override { std::cout << "Derived::setup\n"; }
};

Derived d;   // prints "Base::setup", not "Derived::setup"
```

**Interview answer:** Static binding resolves a function call at compile time from the declared type, enabling inlining and zero overhead; dynamic binding defers resolution to runtime via the vtable so the correct derived-class override runs regardless of the pointer type used to invoke it.
