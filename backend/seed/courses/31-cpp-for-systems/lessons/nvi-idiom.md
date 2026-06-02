# The Non-Virtual Interface (NVI) Idiom

The **Non-Virtual Interface (NVI)** idiom is a C++ design pattern where the public API consists of non-virtual functions, and those functions internally call private (or protected) virtual hooks that derived classes override. Herb Sutter popularized it in "Virtuality" (C++ Users Journal, 2001).

## The Core Idea

- **Public non-virtual method** — the stable contract callers depend on. It owns pre/post conditions, logging, locking, and invariant checks.
- **Private virtual method** — the customization point that subclasses override.

```cpp
class DataSink {
public:
    // Public, non-virtual — callers use this
    int write(const char* buf, std::size_t len) {
        if (!buf || len == 0) return -1;        // pre-condition
        int result = do_write(buf, len);        // virtual dispatch
        ++write_count_;                         // post-condition
        return result;
    }

    int flush() {
        return do_flush();
    }

    virtual ~DataSink() = default;

private:
    // Private, virtual — derived classes override these
    virtual int do_write(const char* buf, std::size_t len) = 0;
    virtual int do_flush() = 0;

    int write_count_ = 0;
};
```

Derived classes override `do_write` and `do_flush`, never `write` or `flush`:

```cpp
class FileSink : public DataSink {
    FILE* fp_;
private:
    int do_write(const char* buf, std::size_t len) override {
        return static_cast<int>(std::fwrite(buf, 1, len, fp_));
    }
    int do_flush() override { return std::fflush(fp_) == 0 ? 0 : -1; }

public:
    explicit FileSink(const char* path) : fp_(std::fopen(path, "wb")) {}
    ~FileSink() override { if (fp_) std::fclose(fp_); }
};
```

## Benefits of NVI

| Benefit | Explanation |
|---------|-------------|
| **Enforced pre/post conditions** | Base always runs validation, logging, locking before/after the virtual call |
| **Stable public API** | Adding instrumentation to `write()` does not require changing any derived class |
| **Separation of concerns** | Interface design (public) is decoupled from customization (private virtual) |
| **Easier to audit** | All cross-cutting concerns live in one place in the base |

## NVI vs Traditional Virtual

Traditional approach — the public function *is* virtual:

```cpp
// Traditional — derived class can bypass pre-conditions by overriding write()
class DataSink {
public:
    virtual int write(const char* buf, std::size_t len) = 0;
};
```

A derived class that overrides `write` gets zero pre-condition checking automatically. NVI prevents this by sealing the public method.

## Private vs Protected Virtuals

The NVI hook can be `private` or `protected`:

- **Private virtual** (preferred) — derived class overrides but cannot call the base hook directly. Enforces that customization only happens through the public wrapper.
- **Protected virtual** — derived class can call `Base::do_write(...)` explicitly, useful when the base hook has default logic the derived class wants to reuse.

```cpp
// Protected — allows Base::do_write call from derived
virtual int do_write(const char* buf, std::size_t len) {
    // Default: discard all data (null device)
    return static_cast<int>(len);
}
```

## NVI in Systems Code

NVI appears naturally in OS scheduler and driver designs:

```cpp
class Scheduler {
public:
    void tick() {          // called by the timer ISR
        update_timers();   // base bookkeeping
        do_schedule();     // virtual: pick next thread
        account_cpu();     // base bookkeeping
    }
private:
    virtual void do_schedule() = 0;
    void update_timers();
    void account_cpu();
};
```

The timer interrupt always invokes `tick()`, guaranteeing that `update_timers()` and `account_cpu()` run regardless of which scheduling policy is active (round-robin, CFS, EDF, etc.).

## Common Pitfall

Calling the public wrapper from within `do_write` creates infinite recursion. Keep the virtual hooks free of calls to their own wrapper.

> **Interview answer:** The NVI idiom makes the public API non-virtual so the base class owns pre/post-condition logic, while derived classes override private virtual hooks for customization — ensuring cross-cutting concerns (validation, logging, locking) cannot be bypassed.
