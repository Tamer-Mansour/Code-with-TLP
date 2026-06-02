# static in Classes: Shared State and Init Order

A `static` data member or member function belongs to the **class itself**, not to any individual object. Every instance shares the same underlying storage.

## static Data Members

```cpp
class Connection {
public:
    static int active_count;   // declaration — not a definition

    Connection()  { ++active_count; }
    ~Connection() { --active_count; }
};

// Definition (in exactly one .cpp file)
int Connection::active_count = 0;
```

- Only one copy exists regardless of how many `Connection` objects are created.
- Must be **defined outside the class** (in exactly one `.cpp` file) unless they are `inline` (C++17) or `constexpr`.

```cpp
// C++17: inline static definition inside the class
class Config {
public:
    inline static int timeout_ms = 5000;  // definition here is fine
};
```

## static Member Functions

A `static` member function has no `this` pointer and can only access other `static` members (or take explicit arguments).

```cpp
class MemPool {
    static uint8_t pool_[4096];
    static size_t  used_;
public:
    static void* allocate(size_t n) {
        if (used_ + n > sizeof(pool_)) return nullptr;
        void* p = pool_ + used_;
        used_ += n;
        return p;
    }
};
```

Call via the class name: `MemPool::allocate(64)` — no object needed.

## Initialization Order Fiasco

Static data members (and other non-local statics) within a single translation unit are initialized in **declaration order**. Across translation units, the order is **unspecified** — this is the infamous *Static Initialization Order Fiasco*.

```cpp
// file1.cpp
int A = 10;

// file2.cpp
extern int A;
int B = A * 2;   // DANGER: A may not be initialized yet if file2 links before file1
```

**Solution:** use the construct-on-first-use idiom for complex statics:

```cpp
class Registry {
public:
    static Registry& instance() {
        static Registry r;   // safe: local static, initialized on first call
        return r;
    }
};
```

## constexpr and inline static Members

```cpp
struct Limits {
    static constexpr int MAX_FDS  = 1024;    // integral constant, no separate definition needed
    static constexpr double EPSILON = 1e-9;  // constexpr double also OK in C++17+
};

int arr[Limits::MAX_FDS];  // fine
```

`constexpr` static members are implicitly `inline` in C++17, so they need no out-of-class definition.

## Thread Safety of Static Members

`static` members are shared across all threads — **no synchronization is implicit**. You must protect shared mutable state yourself:

```cpp
#include <mutex>

class Logger {
    static std::mutex mtx_;
    static int        log_count_;
public:
    static void log(const char* msg) {
        std::lock_guard lock(mtx_);
        ++log_count_;
        // write msg
    }
};
```

## Practical Pattern: Type-Level Counters in Embedded Systems

```cpp
template<typename T>
class InstanceTracker {
    static int count_;
public:
    InstanceTracker()  { ++count_; }
    ~InstanceTracker() { --count_; }
    static int count() { return count_; }
};

template<typename T> int InstanceTracker<T>::count_ = 0;

class Sensor : public InstanceTracker<Sensor> { /* ... */ };
// Sensor::count() returns active sensor objects
```

> **Interview answer:** "`static` class members are shared across all instances; static data members must be defined in exactly one translation unit (unless `inline` in C++17), and access to mutable static members requires explicit synchronization because the compiler provides none."
