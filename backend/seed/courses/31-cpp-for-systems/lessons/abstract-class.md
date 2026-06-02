# What Is an Abstract Class?

An **abstract class** in C++ is any class that contains at least one pure virtual function. It defines an incomplete type — one that captures a concept or contract but deliberately leaves implementation details to derived classes.

## Characteristics at a Glance

| Property | Abstract Class | Concrete Class |
|----------|---------------|----------------|
| Instantiable directly | No | Yes |
| Can have data members | Yes | Yes |
| Can have non-virtual methods | Yes | Yes |
| Can have constructors | Yes (used by derived) | Yes |
| Must override pure virtuals | No — stays abstract | Yes — or stays abstract |

## Anatomy of an Abstract Class

```cpp
class Device {                         // abstract
protected:
    std::string name_;
    bool        open_ = false;

public:
    explicit Device(std::string name) : name_(std::move(name)) {}

    // Pure virtual — every device must define these
    virtual int  read (char* buf, std::size_t len) = 0;
    virtual int  write(const char* buf, std::size_t len) = 0;
    virtual void close() = 0;

    // Non-virtual helper — shared by all devices
    bool is_open() const { return open_; }

    virtual ~Device() = default;
};
```

`Device` cannot be constructed on its own, but it can:

- Hold data (`name_`, `open_`).
- Provide helper functions (`is_open()`).
- Be used as a pointer/reference type for polymorphism.

## Deriving a Concrete Class

```cpp
class UartDevice : public Device {
    int port_;
public:
    UartDevice(std::string name, int port)
        : Device(std::move(name)), port_(port) {}

    int  read (char* buf, std::size_t len) override;
    int  write(const char* buf, std::size_t len) override;
    void close() override;
};
```

Now `UartDevice` is concrete and can be instantiated.

## Abstract Classes vs Interfaces

C++ has no dedicated `interface` keyword. In practice, two patterns are used:

1. **Abstract base with shared state/logic** — has data members and some implementations.
2. **Pure interface class** — all methods pure virtual, no data, models the interface pattern.

The lesson on interface-like classes covers the second pattern in detail.

## When the Compiler Catches You

```cpp
Device d("uart");               // Error: cannot instantiate abstract class
Device* p = new UartDevice(…);  // OK: pointer to abstract type
```

The compiler error message will list every unimplemented pure virtual function — invaluable when a derived class accidentally misses one.

## Abstract Classes in OS / Systems Design

Operating systems and embedded firmware use abstract classes as HAL contracts:

```cpp
class FileSystem {
public:
    virtual int  mount()                              = 0;
    virtual int  open (const char* path, int flags)  = 0;
    virtual int  read (int fd, void* buf, size_t n)  = 0;
    virtual int  write(int fd, const void* buf, size_t n) = 0;
    virtual int  close(int fd)                        = 0;
    virtual void unmount()                            = 0;
    virtual ~FileSystem() = default;
};
```

The kernel's VFS layer holds `FileSystem*` pointers and never knows whether it is talking to ext4, FAT32, or a RAM disk.

## Common Pitfall: Forgetting to Override All Pure Virtuals

If a derived class forgets even one pure virtual, it is still abstract and cannot be instantiated. The compiler error is your friend — read it carefully.

> **Interview answer:** An abstract class is any C++ class with at least one pure virtual function; it cannot be instantiated directly and serves as a blueprint that enforces derived classes to implement the declared interface.
