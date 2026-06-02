# mutable and thread_local

Two less-discussed storage qualifiers — `mutable` and `thread_local` — appear regularly in OS internals, concurrent libraries, and caching layers.

## mutable: Mutability Inside const Objects

`mutable` allows a specific member to be modified even when the enclosing object is `const`. It is used for **logical constness** — the object's externally visible state does not change, but some internal bookkeeping does.

```cpp
class FileReader {
    int         fd_;
    mutable int access_count_ = 0;   // mutable: can be changed even in const methods

public:
    int read(char* buf, int n) const {
        ++access_count_;             // OK because access_count_ is mutable
        return ::read(fd_, buf, n);
    }

    int access_count() const { return access_count_; }
};

const FileReader reader(open("/etc/hosts", O_RDONLY));
reader.read(buf, 64);   // legal even though reader is const
```

### Typical Uses

- **Lazy caches:** compute an expensive value on first access and cache it in a `mutable` member without exposing mutability in the API.
- **Mutex inside a const method:** a mutex must be locked (non-const operation) even in `const` read methods.

```cpp
class SafeCounter {
    mutable std::mutex mtx_;
    int count_ = 0;
public:
    int get() const {
        std::lock_guard lock(mtx_);   // needs to modify mtx_, so it must be mutable
        return count_;
    }
    void increment() {
        std::lock_guard lock(mtx_);
        ++count_;
    }
};
```

### Pitfall: mutable and Logical vs Bitwise Constness

The language only enforces **bitwise constness** (non-mutable members unchanged). `mutable` breaks that rule intentionally. Be careful: overuse of `mutable` can make code hard to reason about. A `const` method with many mutable members is effectively a non-const method with a misleading signature.

## thread_local: Per-Thread Storage Duration

`thread_local` is a storage-class specifier introduced in C++11. Each thread gets its **own independent copy** of the variable, initialized when the thread starts and destroyed when it exits.

```cpp
thread_local int thread_id = -1;  // each thread has its own thread_id

void worker(int id) {
    thread_id = id;    // only affects this thread's copy
    // ...
}
```

### Storage Duration Comparison

| Specifier | Storage | Lifetime |
|---|---|---|
| `auto` (default) | Stack | Block scope |
| `static` (local) | Static segment | Program lifetime |
| `thread_local` | Per-thread segment | Thread lifetime |
| `thread_local static` | Per-thread segment | Thread lifetime (same as thread_local) |

`thread_local` can be combined with `static` or `extern`. Inside a function, `thread_local` implies `static` (the thread-local variable persists across calls within the same thread).

### Practical: Per-Thread Error State

The POSIX `errno` is defined as `thread_local` (or equivalent) so each thread has its own error variable without races:

```cpp
thread_local int my_errno = 0;

int safe_open(const char* path) {
    int fd = open(path, O_RDONLY);
    if (fd == -1) my_errno = errno;
    return fd;
}
```

### Practical: Per-Thread Buffer (Avoiding Synchronization)

```cpp
char* get_format_buffer() {
    thread_local char buf[512];   // each thread owns a private 512-byte buffer
    return buf;
}
```

This avoids mutex overhead — since each thread has its own copy, there is no sharing.

### Pitfall: Initialization Overhead

`thread_local` objects with non-trivial constructors incur initialization cost on first access in each thread. On some platforms, the access mechanism (via a thread-local storage slot) is also slightly more expensive than a regular global access. In hot loops, cache the pointer locally:

```cpp
void hot_path() {
    char* buf = get_format_buffer();   // fetch thread-local pointer once
    for (int i = 0; i < 10000; ++i) {
        // use buf — no repeated TLS lookup
    }
}
```

> **Interview answer:** "`mutable` allows specific members to be modified inside `const` methods, enabling logical constness (caches, mutexes). `thread_local` gives each thread its own independent copy of a variable with thread lifetime — used for per-thread error state, buffers, and avoiding synchronization overhead."
