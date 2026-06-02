# RAII for Files, Sockets, and OS Handles

Operating system handles — file descriptors, socket descriptors, Windows `HANDLE` values, memory-mapped regions — are finite kernel resources. A process that leaks them will eventually fail with `EMFILE`, `ENOMEM`, or similar errors. RAII wrappers turn leak prevention from a discipline into a structural guarantee.

## What Makes OS Handles Special

Unlike heap memory, OS handles:

- Are integers (or opaque pointers), not typed objects — the compiler won't remind you to close them.
- Have distinct "invalid" sentinel values (`-1` for POSIX FDs, `INVALID_HANDLE_VALUE` on Windows, `nullptr` for pointers).
- Are not copyable in the OS sense — duplicating the integer does not duplicate the underlying resource.
- Must be released with a specific call (`close`, `CloseHandle`, `munmap`, `freeaddrinfo`, etc.).

## A POSIX File Descriptor RAII Wrapper

```cpp
#include <unistd.h>
#include <fcntl.h>
#include <stdexcept>

class FileDescriptor {
public:
    explicit FileDescriptor(const char* path, int flags)
        : fd_(::open(path, flags))
    {
        if (fd_ == -1)
            throw std::system_error(errno, std::generic_category(), path);
    }

    ~FileDescriptor() noexcept {
        if (fd_ != -1)
            ::close(fd_);
    }

    // Non-copyable: two objects would share one fd and double-close it
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    // Movable: transfer ownership, leave source invalid
    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ != -1) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    int get() const noexcept { return fd_; }

    // Allow explicit early release
    int release() noexcept {
        int tmp = fd_;
        fd_ = -1;
        return tmp;
    }

private:
    int fd_;
};
```

Usage is clean and leak-proof:

```cpp
void read_config(const char* path) {
    FileDescriptor fd(path, O_RDONLY);
    char buf[256];
    ssize_t n = read(fd.get(), buf, sizeof(buf));
    // fd closes automatically — even if read throws or we return early
}
```

## Socket RAII Wrapper

Sockets are file descriptors on POSIX, so `FileDescriptor` above works as-is. On Windows, sockets are `SOCKET` (an alias for `uintptr_t`) and must be closed with `closesocket`:

```cpp
#include <winsock2.h>

class WinSocket {
public:
    explicit WinSocket(int af, int type, int proto)
        : sock_(::socket(af, type, proto))
    {
        if (sock_ == INVALID_SOCKET)
            throw std::runtime_error("socket() failed");
    }

    ~WinSocket() noexcept {
        if (sock_ != INVALID_SOCKET)
            ::closesocket(sock_);
    }

    WinSocket(const WinSocket&) = delete;
    WinSocket& operator=(const WinSocket&) = delete;

    WinSocket(WinSocket&& o) noexcept : sock_(o.sock_) { o.sock_ = INVALID_SOCKET; }

    SOCKET get() const noexcept { return sock_; }

private:
    SOCKET sock_;
};
```

## Memory-Mapped Files

`mmap` returns a pointer; `munmap` takes the pointer and length. Wrapping it requires storing both:

```cpp
#include <sys/mman.h>

class MappedRegion {
public:
    MappedRegion(void* addr, size_t len, int prot, int flags, int fd, off_t offset)
        : ptr_(::mmap(addr, len, prot, flags, fd, offset)), len_(len)
    {
        if (ptr_ == MAP_FAILED)
            throw std::system_error(errno, std::generic_category(), "mmap");
    }

    ~MappedRegion() noexcept {
        if (ptr_ != MAP_FAILED)
            ::munmap(ptr_, len_);
    }

    MappedRegion(const MappedRegion&) = delete;
    MappedRegion& operator=(const MappedRegion&) = delete;

    void* data() const noexcept { return ptr_; }
    size_t size() const noexcept { return len_; }

private:
    void* ptr_;
    size_t len_;
};
```

## Common Pitfalls

- **Forgetting the invalid sentinel in the move constructor.** If you set `other.fd_` to `0` instead of `-1`, the destructor calls `close(0)` — closing stdin.
- **Copying the wrapper.** Without `= delete`, an accidental copy leads to double-close and use-after-close bugs.
- **Throwing in the destructor.** If `close` fails (e.g., `EIO` on an NFS flush), log the error but do not throw — throwing from a destructor during stack unwinding calls `std::terminate`.

## Using `std::unique_ptr` with a Custom Deleter

For quick wrappers without writing a full class:

```cpp
auto fd_deleter = [](int* p) { if (*p != -1) ::close(*p); delete p; };
std::unique_ptr<int, decltype(fd_deleter)> fd(new int(::open("f", O_RDONLY)), fd_deleter);
```

Or, more idiomatically for `FILE*`:

```cpp
std::unique_ptr<FILE, decltype(&fclose)> f(fopen("f", "r"), fclose);
```

**Interview answer:** An OS handle RAII wrapper stores the handle as a private member, deletes copy operations to prevent double-close, implements move to allow ownership transfer, and calls the correct release function (`close`, `CloseHandle`, `munmap`) in a `noexcept` destructor.
