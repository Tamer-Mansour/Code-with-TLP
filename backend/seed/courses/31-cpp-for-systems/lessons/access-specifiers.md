# Access Specifiers: public, private, protected

Access specifiers are labels inside a class body that control which code can see and use each member. They are C++'s primary tool for **encapsulation** — the practice of hiding implementation details behind a stable interface.

## The Three Specifiers

| Specifier   | Accessible from…                                        |
|-------------|----------------------------------------------------------|
| `public`    | Any code that can see the object                         |
| `private`   | Only the class itself and its `friend`s                  |
| `protected` | The class itself, its `friend`s, and derived classes     |

A specifier applies to all members declared after it until the next specifier or the closing brace.

```cpp
class SensorDriver {
public:                        // ← visible to everyone
    void init();
    int  readValue();

protected:                     // ← visible to subclasses
    void resetHardware();

private:                       // ← internal only
    int  raw_register_ = 0;
    void calibrate();
};
```

## `public` — The Interface

Public members form the **API contract**. Anything you put here is part of the promise you make to callers. Changing a public member's name or signature is a breaking change.

```cpp
class Timer {
public:
    void   start();
    void   stop();
    double elapsedMs() const;
};
```

## `private` — Implementation Details

Private members are invisible to the outside world. They let you change internal representation freely without affecting callers.

```cpp
class Timer {
public:
    void   start()           { running_ = true;  }
    void   stop()            { running_ = false; }
    double elapsedMs() const { return elapsed_us_ / 1000.0; }

private:
    bool     running_    = false;
    uint64_t elapsed_us_ = 0;   // could change to nanoseconds later
    uint64_t start_tick_ = 0;
};
```

If you later switch from microseconds to nanoseconds, only the class internals change — no caller needs to be updated.

## `protected` — Inheritance Bridge

Protected members are hidden from random callers but visible to subclasses. Use them sparingly; exposing implementation details to a whole inheritance hierarchy creates coupling.

```cpp
class BaseDevice {
protected:
    void writeRegister(uint32_t addr, uint32_t val);  // subclasses may use this
private:
    uint32_t base_addr_ = 0;
};

class UartDevice : public BaseDevice {
public:
    void send(uint8_t byte) {
        writeRegister(0x04, byte);  // OK — protected access
    }
};
```

## Multiple Sections Are Allowed

A class may have several `public:`, `private:`, or `protected:` sections. By convention, put `public` first (so readers see the interface first), then `protected`, then `private`.

```cpp
class FileDescriptor {
public:
    explicit FileDescriptor(int fd);
    ~FileDescriptor();
    ssize_t read(void* buf, size_t n);

private:
    int fd_ = -1;
};
```

## Common Pitfalls

- **Over-exposing data as `public`** — callers can set `fd_ = -999` and break the invariant. Prefer private data with accessor methods.
- **Putting everything in `private` then friending everything** — defeats the purpose. If you need that, reconsider your design.
- **Using `protected` data instead of `protected` methods** — subclasses become tightly coupled to the layout. Prefer protected *functions*, not raw data members.

## Worked Example: Memory-Mapped I/O Register

```cpp
class MmioRegister {
public:
    explicit MmioRegister(volatile uint32_t* addr) : reg_(addr) {}

    void     setBit(int bit)    { *reg_ |=  (1u << bit); }
    void     clearBit(int bit)  { *reg_ &= ~(1u << bit); }
    uint32_t read() const       { return *reg_; }

private:
    volatile uint32_t* reg_;    // pointer to hardware register
};

// Usage
MmioRegister gpio(reinterpret_cast<volatile uint32_t*>(0x4002'0000));
gpio.setBit(5);     // pull pin 5 high
// gpio.reg_ = …;  // ERROR — private, hardware pointer is protected
```

The caller manipulates bits through a safe API; the raw pointer is hidden.

---

> **Interview answer:** "`public` members are accessible everywhere; `private` members are accessible only within the class and its `friend`s; `protected` members are additionally accessible in derived classes. Keeping data `private` enforces invariants and decouples callers from implementation details."
