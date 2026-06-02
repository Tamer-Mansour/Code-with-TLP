# RAII Pitfalls: Order, Copies, and Early Release

RAII is robust but not foolproof. Several well-defined pitfalls can silently undermine its guarantees. Knowing them is the difference between code that looks RAII-correct and code that actually is.

## Pitfall 1: Destruction Order Surprises

C++ guarantees that local variables are destroyed in **reverse order of declaration**. Class members are destroyed in **reverse order of declaration in the class body** (not the initializer list order). Violating the expected ordering causes use-after-free bugs.

```cpp
class Server {
    Database db_;        // destroyed LAST (declared first)
    Logger   logger_;    // destroyed FIRST (declared last)
    // BUG: if Logger's destructor tries to write to db_, db_ is already gone
};
```

Fix: declare members in the order you want them destroyed, reversed:

```cpp
class Server {
    Logger   logger_;   // destroyed first — no dependency on db_
    Database db_;       // destroyed second
};
```

Or, redesign so members don't depend on each other in destructors.

## Pitfall 2: Accidental Copies Create Double-Free

If you forget to delete the copy constructor, accidental copies of a RAII object lead to two objects holding the same handle — and the destructor running twice.

```cpp
class FileDescriptor {
    int fd_;
public:
    FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() noexcept { close(fd_); }
    // Copy constructor NOT deleted — default memberwise copy
};

void problem() {
    FileDescriptor a(open("file", O_RDONLY));
    FileDescriptor b = a;   // b.fd_ == a.fd_ — same underlying fd
}   // close() called twice on the same fd — undefined behavior
```

Always delete copy for owning RAII types, or explicitly implement deep copy:

```cpp
FileDescriptor(const FileDescriptor&) = delete;
FileDescriptor& operator=(const FileDescriptor&) = delete;
```

## Pitfall 3: Early Release Without Nulling the Source

Moving a RAII object without properly invalidating the source leaves both objects believing they own the resource:

```cpp
// Incorrect move — forgot to clear source
FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
    // other.fd_ still holds the value — destructor will close it again
}

// Correct
FileDescriptor(FileDescriptor&& other) noexcept
    : fd_(std::exchange(other.fd_, -1)) {}
```

Use `std::exchange` — it sets the source to the sentinel in one atomic step.

## Pitfall 4: Releasing a Resource Too Early via `release()`

A `release()` method transfers ownership to the caller. If the caller forgets to store the raw handle, the resource leaks:

```cpp
FileDescriptor fd("data.bin", O_RDONLY);
fd.release();                      // BUG: returned value discarded — fd leaked
int raw = fd.release();            // OK: caller now responsible
close(raw);
```

Reserve `release()` for interoperability with C APIs that take ownership. In C++ code, prefer moving the wrapper object instead.

## Pitfall 5: Using the Object After Move

After moving from a RAII object, the source is in a valid but empty state. Using it is undefined behavior or a logical error:

```cpp
auto lock = std::make_unique<MutexLock>(mtx);
auto moved = std::move(lock);
lock->unlock();   // BUG: lock is null after move
```

Treat moved-from objects as dead. Avoid storing moved-from objects in variables where they could be accidentally used.

## Pitfall 6: Throwing in the Destructor

```cpp
class TempFile {
    std::string path_;
public:
    ~TempFile() {
        if (std::remove(path_.c_str()) != 0)
            throw std::runtime_error("remove failed");  // NEVER DO THIS
    }
};
```

If this destructor runs during stack unwinding from another exception, `std::terminate` is called. Log the error, do not throw:

```cpp
~TempFile() noexcept {
    if (std::remove(path_.c_str()) != 0)
        fprintf(stderr, "warning: could not remove %s\n", path_.c_str());
}
```

## Pitfall 7: RAII and `std::vector` — Invalidated References

Storing RAII objects in a `std::vector` and then resizing it moves (or copies) the elements. If you kept a raw pointer or reference to an element, it is now dangling:

```cpp
std::vector<FileDescriptor> fds;
fds.emplace_back(open("a", O_RDONLY));
int* raw = &fds[0].fd_;            // reference into vector
fds.emplace_back(open("b", O_RDONLY));  // may reallocate — raw is dangling
```

Use indices, not pointers, into vectors. Or `reserve` enough capacity upfront.

## Quick Reference: Pitfalls and Fixes

| Pitfall | Symptom | Fix |
|---|---|---|
| Wrong destruction order | Use-after-free in destructor | Order members carefully; check dependencies |
| Accidental copy | Double-free / double-close | `= delete` copy constructor and assignment |
| Move without nulling source | Double-free | Use `std::exchange(other.h_, sentinel)` |
| Discarded `release()` return value | Resource leak | `[[nodiscard]]` on `release()` |
| Use-after-move | Null dereference or logic error | Treat moved-from as dead |
| Throw in destructor | `std::terminate` on stack unwind | Mark `noexcept`, log instead of throw |
| Vector reallocation | Dangling pointer | Use indices or `reserve` |

**Interview answer:** The most common RAII pitfalls are member destruction-order surprises, failing to delete copy to prevent double-free, and not nulling the moved-from handle — all of which cause undefined behavior that is often not caught until production.
