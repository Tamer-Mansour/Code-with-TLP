# Pointers, References, and Memory

SystemC modules connect to each other through ports that hold **pointers** to channel objects under the hood. TLM sockets pass **references** to generic payloads. Understanding the difference between a pointer and a reference — and knowing when each is appropriate — is essential for reading and writing SystemC models correctly.

## Pointers

A pointer is a variable that stores the **memory address** of another object.

```cpp
int  x   = 42;
int* ptr = &x;    // ptr holds the address of x

*ptr = 99;        // dereference: changes x to 99
std::cout << x;   // prints 99
```

Key operations:

| Syntax | Meaning |
|--------|---------|
| `&x`   | Address-of: produces the address of `x` |
| `*ptr` | Dereference: accesses the object at the address |
| `ptr->member` | Shorthand for `(*ptr).member` |
| `ptr == nullptr` | Null check — always do this before dereferencing |

Pointers can be reassigned and can be null. They are used when you need optional association, arrays, or dynamic allocation.

## References

A reference is an **alias** for an existing object. It must be bound at declaration and cannot be rebound.

```cpp
int  a = 10;
int& ref = a;   // ref IS a

ref = 20;       // changes a to 20
```

References have no null state and no address-of overhead in normal use, making them the preferred choice for function parameters when you want to avoid copying without risking a null dereference.

```cpp
// Pass by value — copies the whole payload
void slow(tlm::tlm_generic_payload payload);

// Pass by reference — no copy, caller's object is modified
void fast(tlm::tlm_generic_payload& payload);

// Pass by const reference — no copy, read-only
void read_only(const tlm::tlm_generic_payload& payload);
```

## Dynamic Memory

Objects can be allocated on the **heap** with `new` and must be freed with `delete`.

```cpp
int* arr = new int[64];   // heap array
arr[0]   = 1;
delete[] arr;             // must match new[]
```

In modern C++ you almost never call `new` directly. Use:

- `std::unique_ptr<T>` — sole ownership, freed automatically on scope exit
- `std::shared_ptr<T>` — shared ownership with reference counting
- `std::vector<T>` — resizable heap array, manages its own memory

## Pointers in SystemC

Port binding works through pointer indirection inside the library:

```cpp
SC_MODULE(Top) {
    Adder*      adder;
    sc_signal<int> sig_a, sig_b, sig_out;

    SC_CTOR(Top) {
        adder = new Adder("adder");   // dynamic module creation
        adder->a(sig_a);
        adder->b(sig_b);
        adder->result(sig_out);
    }

    ~Top() {
        delete adder;   // manual cleanup (or use unique_ptr)
    }
};
```

A common modern pattern is:

```cpp
std::unique_ptr<Adder> adder;

SC_CTOR(Top) : adder(std::make_unique<Adder>("adder")) {
    adder->a(sig_a);
    ...
}
// No destructor needed — unique_ptr deletes automatically
```

## TLM and References

TLM 2.0 transports pass `tlm_generic_payload` by **reference** to avoid expensive copies of a struct that can hold megabytes of data:

```cpp
virtual void b_transport(tlm::tlm_generic_payload& trans,
                          sc_time& delay) {
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

Both `trans` and `delay` are modified by the callee — only a reference allows this without the overhead of returning a struct.

## Common Pitfalls

- **Dangling pointer** — using a pointer after the object it points to has been destroyed. This causes undefined behaviour, often a crash.
- **Null dereference** — calling `->` on a null pointer. Always check `ptr != nullptr`.
- **Memory leak** — calling `new` without a matching `delete`. Use smart pointers to eliminate this class of bug.
- **Reference to temporary** — binding a non-const reference to a temporary is a compilation error; binding a `const` reference extends the temporary's lifetime but only to the end of the enclosing scope.

## Pointer vs Reference — Quick Guide

| Want... | Use |
|---------|-----|
| Optional association (may be null) | Pointer |
| Always-valid alias, no rebind | Reference |
| Read-only, no copy | `const T&` |
| Ownership transfer | `std::unique_ptr<T>` |
| Shared ownership | `std::shared_ptr<T>` |

> **Interview answer:** A pointer stores an address, can be null, and can be reassigned; a reference is an alias that must be bound at declaration and cannot be null. In SystemC, dynamic module instantiation uses raw or smart pointers, while TLM transport functions pass the generic payload by reference to allow in-place modification without copying.
