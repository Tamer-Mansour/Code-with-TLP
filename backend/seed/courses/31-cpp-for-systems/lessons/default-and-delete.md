# = default and = delete on Special Members

C++11 gave programmers two new keywords to explicitly control the **special member functions**: default constructor, destructor, copy constructor, copy-assignment operator, move constructor, and move-assignment operator.

## The Problem They Solve

The compiler silently generates these members when you don't declare them, and silently suppresses them when you do declare certain others. The implicit rules are subtle and error-prone. `= default` and `= delete` make intent explicit and visible in the class definition.

## `= default`

`= default` asks the compiler to generate the standard ("defaulted") implementation even when it would otherwise be suppressed. It can appear either inside the class definition (inline) or outside with the definition syntax.

```cpp
class Config {
public:
    Config() = default;               // explicit default constructor
    Config(const Config&) = default;  // copy is fine
    Config& operator=(const Config&) = default;
    ~Config() = default;
};
```

**Why bother if the compiler does it anyway?**

1. **Documentation:** future readers see that the omission is intentional.
2. **Restoring suppressed defaults:** declaring *any* constructor suppresses the implicit default. `= default` brings it back explicitly.

```cpp
class Server {
    int port;
public:
    Server(int p) : port(p) {}   // user constructor suppresses default
    Server() = default;          // explicitly restore default constructor
};
```

3. **Trivial special members:** a `= default`-ed constructor defined inside the class is *trivial* (for POD-like optimizations), whereas a user-written `{}` body is not.

## `= delete`

`= delete` marks a function as explicitly deleted. Calling or selecting it in overload resolution is a **compile-time error** with a clear diagnostic. You can delete any function — not just special members.

```cpp
class Singleton {
public:
    static Singleton& instance() {
        static Singleton s;
        return s;
    }

    Singleton(const Singleton&)            = delete;
    Singleton& operator=(const Singleton&) = delete;
    Singleton(Singleton&&)                 = delete;
    Singleton& operator=(Singleton&&)      = delete;
private:
    Singleton() = default;
};
```

### Common Uses of `= delete`

**Prevent copies for resource-owning types:**

```cpp
class FileDescriptor {
    int fd;
public:
    explicit FileDescriptor(int fd) : fd(fd) {}
    ~FileDescriptor() { close(fd); }

    FileDescriptor(const FileDescriptor&)            = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    // Allow moves
    FileDescriptor(FileDescriptor&& o) : fd(o.fd) { o.fd = -1; }
};
```

**Block unintended implicit conversions:**

```cpp
class Sensor {
public:
    explicit Sensor(int id);
    void calibrate(double value);
    void calibrate(int) = delete;   // prevent silent int→double conversion
};

Sensor s(1);
s.calibrate(1);     // ERROR: calibrate(int) is deleted
s.calibrate(1.0);   // OK
```

**Disable heap allocation:**

```cpp
class StackOnly {
public:
    void* operator new(std::size_t) = delete;
    void  operator delete(void*)    = delete;
};

StackOnly s;          // OK
StackOnly* p = new StackOnly(); // compile error
```

## Interaction with the Rule of Five

| You declare | Compiler generates |
|---|---|
| Destructor | Copy ops: yes (deprecated). Move ops: **no** |
| Copy constructor | Copy-assign: yes. Move ops: **no** |
| Move constructor | Copy ops: **deleted**. Move-assign: **no** |
| Move assignment | Copy ops: **deleted**. Move constructor: **no** |

Use `= default` and `= delete` to opt in or out of each operation precisely.

```cpp
class Buffer {
    std::unique_ptr<int[]> data;
    std::size_t size;
public:
    Buffer(std::size_t n) : data(new int[n]), size(n) {}

    // No copies — unique_ptr is move-only anyway, but be explicit:
    Buffer(const Buffer&)            = delete;
    Buffer& operator=(const Buffer&) = delete;

    // Moves are fine (defaulted):
    Buffer(Buffer&&)            = default;
    Buffer& operator=(Buffer&&) = default;

    ~Buffer() = default;
};
```

## Pitfall: `= delete` in Overload Sets

A deleted overload still participates in overload resolution. If it is the best match, the call is an error — even if a non-deleted overload could have been called with a conversion.

```cpp
void process(long);
void process(int) = delete;

process(42);    // ERROR: int overload is best match and it is deleted
process(42L);   // OK: calls process(long)
```

This is intentional: it prevents silent narrowing conversions.

> **Interview answer:** `= default` asks the compiler to generate the standard implementation of a special member, even when it would be suppressed by another declaration. `= delete` makes the function a compile-time error if selected, used to prevent copies, dangerous conversions, or heap allocation. Both make intent explicit rather than relying on the compiler's implicit suppression rules.
