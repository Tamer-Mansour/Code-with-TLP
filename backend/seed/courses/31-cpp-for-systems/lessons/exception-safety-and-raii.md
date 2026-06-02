# Exception Safety Guarantees Through RAII

When an exception propagates, the C++ runtime unwinds the call stack, destroying all local objects with automatic storage duration in reverse order of construction. RAII exploits this guarantee to make cleanup automatic under any failure condition. Understanding the three levels of exception safety is essential for writing correct system code.

## The Three Levels of Exception Safety

### 1. Basic Guarantee

If an exception is thrown, the program remains in a **valid but unspecified** state. No resources are leaked, no invariants are violated, but the exact state of objects is not guaranteed. Most RAII-based code provides this automatically.

### 2. Strong Guarantee (Commit-or-Rollback)

If an exception is thrown, the operation has **no observable effect** — the state is exactly as it was before the call. This is the transactional ideal. Achieved by operating on copies and then doing a no-throw swap.

### 3. No-Throw Guarantee

The operation **never throws**. Required for destructors, move constructors, and swap. Mark these `noexcept`.

## How RAII Provides the Basic Guarantee Automatically

Consider allocating two resources:

```cpp
void setup() {
    auto conn = std::make_unique<DbConnection>("localhost");  // may throw
    auto cache = std::make_unique<Cache>(1024 * 1024);       // may throw
    // ...
}
```

If `Cache` constructor throws, `conn` is already constructed. Stack unwinding destroys `conn` — its `unique_ptr` destructor closes the database connection. No leak. No manual cleanup. This is the basic guarantee for free.

Contrast with raw pointers:

```cpp
void setup_broken() {
    DbConnection* conn = new DbConnection("localhost");
    Cache* cache = new Cache(1024 * 1024);  // throws → conn is leaked
    // ...
    delete cache;
    delete conn;
}
```

## Achieving the Strong Guarantee: Copy-and-Swap

```cpp
class Config {
    std::vector<std::string> entries_;
public:
    void update(const std::vector<std::string>& new_entries) {
        // Work on a copy — if any step throws, *this is unchanged
        std::vector<std::string> temp = new_entries;  // may throw — ok
        validate(temp);                               // may throw — ok, temp destroyed
        entries_.swap(temp);                          // noexcept swap
    }
};
```

The swap is the only mutation of `entries_`. Because `std::vector::swap` is `noexcept`, the final commit step cannot throw. The object is either fully updated or completely unchanged.

## Exception Safety in Constructors

A constructor that throws must not leak resources it has already acquired. RAII members handle this automatically because the destructor of a successfully constructed sub-object is called during stack unwinding:

```cpp
class Server {
    FileDescriptor log_fd_;   // RAII wrapper — closes fd in destructor
    std::unique_ptr<Socket> listen_sock_;

    Server(const char* log_path, int port)
        : log_fd_(log_path, O_WRONLY | O_CREAT)   // (1) acquire log fd
        , listen_sock_(std::make_unique<Socket>(port))  // (2) may throw
    {}
    // If (2) throws: log_fd_ is already constructed, its destructor runs — fd closed
};
```

If you use raw members and a member constructor throws, you must handle cleanup manually in a try/catch inside the constructor body — a significant source of bugs.

## The Role of `noexcept`

Marking functions `noexcept` is not just documentation — it enables optimizations and is checked at compile time. If a `noexcept` function propagates an exception, `std::terminate` is called immediately.

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    Buffer(Buffer&& other) noexcept   // MUST be noexcept for std::vector to use move
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }
    ~Buffer() noexcept { delete[] data_; }
};
```

`std::vector` uses move operations only when they are `noexcept`. If a move constructor might throw, the vector falls back to copying, which can be dramatically slower.

## Pitfall: Throwing in Destructors

```cpp
class BadFile {
    int fd_;
public:
    ~BadFile() {
        if (close(fd_) == -1)
            throw std::runtime_error("close failed");  // DANGEROUS
    }
};
```

If this destructor runs during stack unwinding triggered by another exception, a second exception is thrown while one is already active. The result is `std::terminate`. Always swallow or log errors in destructors — never throw.

## Summary Table

| Guarantee | Meaning | How to Achieve |
|---|---|---|
| No-throw | Never throws | `noexcept`; destructors, moves, swaps |
| Strong | No observable effect on failure | Copy-and-swap idiom |
| Basic | Valid state, no leaks | RAII members everywhere |
| None | May leave broken state | Raw pointers, manual cleanup |

**Interview answer:** RAII provides at least the basic exception-safety guarantee automatically: because destructors run during stack unwinding, every successfully constructed RAII member is cleaned up even if a later constructor throws.
