# What Is Abstraction and How It Differs from Encapsulation

Abstraction and encapsulation are often mentioned in the same breath, but they answer different questions:

- **Abstraction** asks: *what does this thing do?* It is about expressing ideas at the right level and hiding irrelevant detail from the consumer's mental model.
- **Encapsulation** asks: *how do I protect this thing's state?* It is a mechanism — access specifiers, private members, controlled mutators.

A clean mental model: **abstraction is a design goal; encapsulation is one of the tools that implements it**.

## Abstraction in Practice

When you write `std::sort(v.begin(), v.end())` you are using an abstraction. You do not care whether it is introsort, heapsort, or insertion sort under the hood. The abstraction is the *contract*: given a range with a comparator, produce a sorted range.

Abstraction manifests in C++ through:

| Mechanism | What it hides |
|---|---|
| Free functions / APIs | Implementation algorithm |
| Classes | Data layout and invariants |
| Interfaces (pure-virtual base) | Concrete type entirely |
| Templates / concepts | Specific type requirements |
| Header vs. translation unit | Compilation details |

## A Concrete Contrast

```cpp
// Encapsulation WITHOUT meaningful abstraction
class Wrapper {
public:
    void set_x(int v) { x_ = v; }
    int  get_x() const { return x_; }
private:
    int x_;
};
// We hid `x_` but the caller still thinks in terms of raw integers.
// This is encapsulation; it barely abstracts anything.
```

```cpp
// Encapsulation WITH abstraction
class Timer {
public:
    void   start();
    void   stop();
    double elapsed_ms() const;
private:
    // Could be POSIX clock_gettime, Win32 QueryPerformanceCounter,
    // or std::chrono — the caller does not know or care.
    std::chrono::steady_clock::time_point start_;
    bool running_ = false;
};
```

`Timer` raises the level of discourse: you think in "start / stop / elapsed", not in platform-specific timestamps.

## Levels of Abstraction in Systems Code

Systems programmers deal with multiple abstraction layers daily:

```
Application logic
      |
 File system API   (open / read / write / close)
      |
 VFS layer         (Linux kernel: struct file_operations)
      |
 Block driver      (submit_bio)
      |
 Hardware registers
```

Each layer hides the one below. A bug in the wrong layer — say, hardware details leaking into application code — is a **leaky abstraction**, one of the most common design smells.

## Common Pitfalls

- **Wrong abstraction level** — a "file" abstraction that exposes disk sector numbers leaks implementation detail.
- **Over-abstraction** — wrapping a one-line call in three virtual dispatch layers for no gain adds overhead and mental load.
- **Premature abstraction** — designing a generic interface before you have two concrete use cases is YAGNI (You Aren't Gonna Need It).

## Worked Example: GPIO Driver Interface

```cpp
// Abstraction: callers think "pin high / pin low"
class GpioPin {
public:
    virtual ~GpioPin() = default;
    virtual void set_high() = 0;
    virtual void set_low()  = 0;
    virtual bool read()     = 0;
};

// Concrete implementation: one per platform
class RpiGpioPin : public GpioPin {
public:
    explicit RpiGpioPin(int pin) : pin_(pin) { /* mmap /dev/gpiomem */ }
    void set_high() override { /* write bit to memory-mapped register */ }
    void set_low()  override { /* clear bit */ }
    bool read()     override { /* read bit */ return false; }
private:
    int pin_;
    volatile uint32_t* reg_ = nullptr;
};
```

Tests can inject a `MockGpioPin` without touching real hardware. The application layer never sees a register address.

## Interview Answer

> "Abstraction is about exposing only the relevant operations for a given level of the system and hiding everything else — it is a design concern. Encapsulation is the C++ mechanism (private members, controlled access) that enforces those boundaries at compile time."
