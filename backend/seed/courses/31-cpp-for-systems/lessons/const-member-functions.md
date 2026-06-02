# const Member Functions and const Correctness

**const correctness** is the discipline of marking every function that does not modify an object with the `const` keyword. It is a zero-cost safety net: the compiler rejects accidental mutations and enables callers to pass objects as `const` references without losing functionality.

## Declaring a `const` Member Function

Append `const` after the parameter list and before the body:

```cpp
class Packet {
public:
    uint16_t sourcePort() const { return src_port_; }  // const method
    void     setSourcePort(uint16_t p) { src_port_ = p; } // non-const method
private:
    uint16_t src_port_ = 0;
};
```

Inside a `const` method, `this` has type `const Packet*`. Any attempt to modify a data member is a compile-time error.

```cpp
uint16_t Packet::sourcePort() const {
    src_port_ = 9999;  // ERROR: assignment of member in read-only object
    return src_port_;
}
```

## Why `const` Correctness Matters

### It enables `const` references and pointers

```cpp
void printPacketInfo(const Packet& p) {
    // Only const methods may be called on p
    std::cout << p.sourcePort() << '\n';  // OK — sourcePort() is const
    p.setSourcePort(80);                  // ERROR — non-const method on const ref
}
```

If `sourcePort()` were not marked `const`, the compiler would reject even the read — forcing callers to take non-const references to perform innocent reads.

### It documents intent

A `const` method is a promise: "I will not change this object's observable state." Readers of the header can trust it.

## const Overloading

You can provide two overloads of the same method — one `const`, one not — and the compiler picks the right one based on the constness of the object:

```cpp
class Buffer {
public:
    uint8_t&       operator[](size_t i)       { return data_[i]; }  // writable
    const uint8_t& operator[](size_t i) const { return data_[i]; }  // read-only
private:
    uint8_t data_[1500] {};
};

Buffer       b;
const Buffer cb;

b[0]  = 0xFF;   // calls non-const overload — OK
cb[0] = 0xFF;   // calls const overload — ERROR: can't assign to const ref
```

## `mutable`: The Escape Hatch

Sometimes a member must change even inside a logically `const` operation — a cache, a mutex, a lazy-initialised value. Mark such members `mutable`:

```cpp
class TemperatureSensor {
public:
    int readCelsius() const {
        if (!cached_) {
            cached_value_ = fetchFromHardware();  // side-effect, but logical const
            cached_ = true;
        }
        return cached_value_;
    }
private:
    mutable int  cached_value_ = 0;
    mutable bool cached_       = false;

    int fetchFromHardware() const;
};
```

Use `mutable` sparingly and document why. Overusing it undermines the guarantees `const` provides.

## `constexpr` Member Functions

`constexpr` methods can be evaluated at compile time and are implicitly `const` (in C++11/14):

```cpp
class Circle {
public:
    constexpr explicit Circle(double r) : radius_(r) {}
    constexpr double area()   const { return 3.14159265 * radius_ * radius_; }
    constexpr double radius() const { return radius_; }
private:
    double radius_;
};

constexpr Circle c(5.0);
constexpr double a = c.area();  // computed at compile time
```

## Common Pitfalls

| Pitfall | Effect | Fix |
|---------|--------|-----|
| Forgetting `const` on accessors | Cannot pass objects as `const&` to functions | Add `const` suffix to all pure-read methods |
| Returning non-`const` reference from `const` method | Callers can modify internal state | Return `const` reference or value |
| Overusing `mutable` | Hides real mutations from `const` analysis | Only use for caches and synchronisation primitives |

## Worked Example: Register Map Reader

```cpp
class RegisterMap {
public:
    explicit RegisterMap(const volatile uint32_t* base, size_t count)
        : base_(base), count_(count) {}

    uint32_t read(size_t idx) const {
        if (idx >= count_) return 0;
        return base_[idx];   // reading hardware — logically const
    }

    size_t count() const { return count_; }

private:
    const volatile uint32_t* base_;
    size_t                   count_;
};

void dumpRegisters(const RegisterMap& regs) {
    for (size_t i = 0; i < regs.count(); ++i)
        printf("reg[%zu] = 0x%08X\n", i, regs.read(i));
}
```

Both `read()` and `count()` are `const`, so `dumpRegisters` can safely accept a `const RegisterMap&` — no copy, no mutation risk.

---

> **Interview answer:** "A `const` member function guarantees it will not modify the object's observable state. It makes the function callable on `const` objects and references, enables const overloading, and documents intent. The compiler enforces the guarantee — any accidental write to a member is a compile error."
