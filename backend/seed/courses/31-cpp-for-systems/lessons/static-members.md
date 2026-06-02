# static Data Members and static Methods

`static` class members belong to the **class itself**, not to any individual object. There is exactly one copy of a static data member, shared by all instances, and static methods can be called without an object at all.

## Static Data Members

A static data member is declared inside the class body but must be **defined** (and optionally initialised) exactly once in a `.cpp` file — otherwise the linker will complain about an undefined symbol.

```cpp
// device.hpp
class Device {
public:
    static int instanceCount;     // declaration — no storage here
    Device()  { ++instanceCount; }
    ~Device() { --instanceCount; }
};

// device.cpp
int Device::instanceCount = 0;   // definition — storage lives here
```

All `Device` objects share the single `instanceCount` variable.

### In-class Initialisation (C++17 `inline`)

C++17 allows `inline` static members to be defined and initialised inside the class:

```cpp
class Device {
public:
    inline static int instanceCount = 0;  // definition + init in one place
};
```

For `const` integral types, in-class initialisation has been allowed since C++11:

```cpp
class Limits {
public:
    static constexpr size_t MAX_DEVICES = 64;  // integral constant — no .cpp needed
};
```

## Static Member Functions

Static methods do not receive a `this` pointer. They can access only:

- Other static members of the class.
- Arguments passed explicitly.
- Free variables with adequate visibility.

```cpp
class Logger {
public:
    static void setLevel(int level) { level_ = level; }
    static int  level()             { return level_;  }

    void log(const char* msg) const {
        if (level_ >= 1)
            printf("[LOG] %s\n", msg);
    }

private:
    static int level_;   // one level setting for all loggers
};

int Logger::level_ = 0;

// Call without an object:
Logger::setLevel(2);
```

## Common Uses in Systems Programming

### Singleton (controlled global)

```cpp
class Scheduler {
public:
    static Scheduler& instance() {
        static Scheduler sched;   // created once, on first call
        return sched;
    }

    void schedule(Task* t);

private:
    Scheduler() = default;
};

Scheduler::instance().schedule(myTask);
```

### Factory method

```cpp
class MemoryPool {
public:
    static MemoryPool* create(size_t blockSize, size_t blockCount);
private:
    MemoryPool(size_t bs, size_t bc);
};
```

### Class-wide constants

```cpp
class DmaController {
public:
    static constexpr uint32_t BASE_ADDR   = 0x4002'6000;
    static constexpr size_t   MAX_CHANNELS = 8;
};
```

Accessing these requires no object: `DmaController::MAX_CHANNELS`.

## Object Count Example (Worked)

```cpp
#include <cstdio>

class Connection {
public:
    static int active() { return count_; }

    Connection()  { ++count_; printf("Open  [total=%d]\n", count_); }
    ~Connection() { --count_; printf("Close [total=%d]\n", count_); }

private:
    inline static int count_ = 0;
};

int main() {
    Connection a, b;
    {
        Connection c;
    }   // c destroyed here
    printf("Active: %d\n", Connection::active());  // 2
}
```

Output:
```
Open  [total=1]
Open  [total=2]
Open  [total=3]
Close [total=2]
Active: 2
```

## Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Forgetting the out-of-class definition (pre-C++17) | Linker error: undefined symbol | Add definition in one `.cpp` |
| Accessing `this` from a static method | Compile error — no `this` | Pass the object as a parameter |
| Static mutable data in a multithreaded program | Data race | Protect with `std::mutex` or `std::atomic` |

---

> **Interview answer:** "Static data members are class-scoped variables shared by all instances — there is exactly one copy. Static methods can be called without an object and have no `this` pointer, so they may only access static members or their arguments. Both are useful for class-wide counters, constants, singletons, and factory methods."
