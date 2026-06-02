# Interface-Like Classes in C++

C++ has no `interface` keyword, but the language's virtual function machinery lets you model the same concept precisely. An **interface-like class** is an abstract class where:

- Every method is pure virtual (no concrete implementations).
- There are no data members.
- The destructor is `virtual` and either defaulted or empty.

This mirrors Java/C# interfaces almost exactly.

## The Pattern

```cpp
// ILogger — pure interface, zero data, all pure virtual
class ILogger {
public:
    virtual void log(int level, const char* message) = 0;
    virtual void flush()                             = 0;
    virtual ~ILogger() = default;       // must be virtual!
};
```

Any class that publicly inherits `ILogger` and overrides both methods becomes a concrete logger:

```cpp
class ConsoleLogger : public ILogger {
public:
    void log(int level, const char* message) override {
        std::printf("[%d] %s\n", level, message);
    }
    void flush() override { std::fflush(stdout); }
};

class FileLogger : public ILogger {
    FILE* fp_;
public:
    explicit FileLogger(const char* path) : fp_(std::fopen(path, "a")) {}
    void log(int level, const char* message) override {
        std::fprintf(fp_, "[%d] %s\n", level, message);
    }
    void flush() override { std::fflush(fp_); }
    ~FileLogger() override { std::fclose(fp_); }
};
```

The caller depends only on `ILogger*` and never on the concrete type:

```cpp
void process(ILogger* logger) {
    logger->log(1, "Starting process");
    // ... work ...
    logger->log(1, "Done");
    logger->flush();
}
```

## Multiple Interface Inheritance

Unlike single abstract base classes that own state, pure interfaces compose cleanly via multiple inheritance:

```cpp
class IReadable {
public:
    virtual int read(char* buf, std::size_t n) = 0;
    virtual ~IReadable() = default;
};

class IWritable {
public:
    virtual int write(const char* buf, std::size_t n) = 0;
    virtual ~IWritable() = default;
};

class IStream : public IReadable, public IWritable {};  // combined interface

class TcpSocket : public IStream {
public:
    int read (char* buf, std::size_t n) override { /* … */ return 0; }
    int write(const char* buf, std::size_t n) override { /* … */ return 0; }
};
```

Because the interface classes have no data, the dreaded diamond problem does not apply — there is nothing to share.

## Interface vs Abstract Base — When to Use Which

| Criterion | Pure Interface | Abstract Base with Shared Logic |
|-----------|---------------|--------------------------------|
| No shared data/logic | Yes | No |
| Multiple inheritance safe | Yes | Risky if data involved |
| Common helpers (e.g., retry logic) | No | Yes |
| Runtime overhead | Same (one vtable per class) | Same |

## Naming Convention

Many C++ codebases prefix interface classes with `I` (`IDevice`, `ILogger`, `IStream`) to signal at a glance that the class is a pure interface with no state. This is a convention, not a language rule.

## Common Pitfall: Non-Virtual Destructor

Forgetting the virtual destructor on an interface causes undefined behaviour when a derived object is deleted through a base pointer:

```cpp
ILogger* logger = new FileLogger("app.log");
delete logger;   // UB if ILogger::~ILogger is not virtual!
```

Always declare `virtual ~IInterface() = default;` on every interface.

> **Interview answer:** An interface-like class in C++ is an abstract class with only pure virtual functions and no data members — it enforces a contract without imposing state, and it composes safely through multiple inheritance.
