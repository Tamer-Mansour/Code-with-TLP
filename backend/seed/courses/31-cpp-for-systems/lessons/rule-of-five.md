# The Rule of Five

The **Rule of Five** extends the classic Rule of Three to cover C++11 move semantics. If your class manages a resource and you need to customize any one of the five special member functions, you almost certainly need to define all five.

## The Five Special Member Functions

```cpp
class Resource {
public:
    Resource();                              // Default constructor (not one of the five)
    ~Resource();                             // 1. Destructor
    Resource(const Resource&);              // 2. Copy constructor
    Resource& operator=(const Resource&);   // 3. Copy assignment
    Resource(Resource&&) noexcept;          // 4. Move constructor
    Resource& operator=(Resource&&) noexcept; // 5. Move assignment
};
```

## Why All Five?

When you define a destructor, the compiler knows the class manages something (memory, a file handle, a mutex). The implicitly generated copy and move operations will be incorrect or suppressed:

- Defining a **destructor** suppresses the implicit move constructor and move assignment (deprecated in C++11 for copy, error-prone in practice).
- Defining a **copy constructor or copy assignment** implicitly deletes the move operations in C++11.
- Defining any **move operation** implicitly deletes the copy operations.

The result: neglect one member, and your class silently falls back to expensive copies or fails to compile.

## Worked Example: FileHandle

```cpp
#include <cstdio>
#include <utility>
#include <stdexcept>

class FileHandle {
    FILE* file_;

public:
    explicit FileHandle(const char* path, const char* mode)
        : file_(std::fopen(path, mode)) {
        if (!file_) throw std::runtime_error("cannot open file");
    }

    // 1. Destructor
    ~FileHandle() {
        if (file_) std::fclose(file_);
    }

    // 2. Copy constructor — files are not copyable; delete it
    FileHandle(const FileHandle&) = delete;

    // 3. Copy assignment — delete for same reason
    FileHandle& operator=(const FileHandle&) = delete;

    // 4. Move constructor
    FileHandle(FileHandle&& other) noexcept
        : file_(other.file_) {
        other.file_ = nullptr;
    }

    // 5. Move assignment
    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this == &other) return *this;
        if (file_) std::fclose(file_); // release current
        file_       = other.file_;
        other.file_ = nullptr;
        return *this;
    }

    FILE* get() const { return file_; }
};
```

Deleting the copy operations is explicit and correct here — file handles are a uniquely-owned, non-copyable resource (like `std::unique_ptr`).

## Compiler Generation Rules (Summary Table)

| User defines | Destructor | Copy ctor | Copy assign | Move ctor | Move assign |
|---|---|---|---|---|---|
| Nothing | Generated | Generated | Generated | Generated | Generated |
| Destructor | User | Generated* | Generated* | Deleted | Deleted |
| Copy ctor | Generated | User | Generated* | Deleted | Deleted |
| Copy assign | Generated | Generated* | User | Deleted | Deleted |
| Move ctor | Generated | Deleted | Deleted | User | Deleted |
| Move assign | Generated | Deleted | Deleted | Deleted | User |

*Generated but deprecated or problematic — do not rely on it.

## Pitfall: Partial Definition Leaves Moves as Copies

```cpp
class Naive {
    int* data_;
public:
    Naive(int n)  : data_(new int[n]) {}
    ~Naive()      { delete[] data_; }
    // Copy/move not defined — compiler provides copy but deletes move
};

Naive a(10);
Naive b = std::move(a); // Falls back to COPY (if copy ctor exists)
                        // Double free when both destructors run!
```

Without a user-defined copy constructor, the compiler provides a member-wise copy, giving both `a` and `b` the same `data_` pointer — a classic double-free bug.

## Practical Guideline

- **Never define just the destructor.** Always pair it with all five, even if the copy/move operations are `= delete`.
- **Use `= delete` explicitly** for non-copyable types rather than leaving copies implicit.
- **Use `= default` explicitly** when the compiler-generated behavior is correct, to document your intent.

```cpp
class SafeResource {
    // ...
public:
    ~SafeResource()                                   = default;
    SafeResource(const SafeResource&)                 = default;
    SafeResource& operator=(const SafeResource&)      = default;
    SafeResource(SafeResource&&) noexcept             = default;
    SafeResource& operator=(SafeResource&&) noexcept  = default;
};
```

> **Interview answer:** The Rule of Five states that if you explicitly define any one of destructor, copy constructor, copy assignment, move constructor, or move assignment, you should define all five — because defining one suppresses or corrupts the compiler-generated forms of the others, leading to double-free bugs, leaks, or silent fallback to copies.
