# Double Free and Heap Corruption

## What Is a Double Free?

A double free happens when `delete` (or `free`) is called more than once on the same pointer value. After the first `delete`, the memory is returned to the allocator's internal free-list. The second `delete` passes that same address back to the allocator, which now treats it as if it were a live allocation — corrupting the internal metadata that tracks free blocks.

```cpp
int* p = new int(42);
delete p;   // correct: memory returned to allocator
delete p;   // UNDEFINED BEHAVIOR: double free
```

## Why It Is So Dangerous

Heap allocators maintain linked lists or trees of free blocks. When you `delete` a pointer, the allocator writes bookkeeping data (e.g., size, next-free-pointer) into the freed region. A second `delete` on the same address makes the allocator believe it is processing a valid free block — it reads and writes those bookkeeping fields again. The result:

- **Silent heap metadata corruption** — future allocations or deallocations use corrupted data.
- **Heap layout control by an attacker** — in security exploits, a double-free can be used to manipulate the free-list so that a subsequent `malloc` returns a region that overlaps with a security-critical data structure.
- **Crash at an unrelated site** — symptoms appear far from the actual bug.

## Common Causes

### Aliased Raw Pointers

```cpp
int* a = new int(1);
int* b = a;    // both point to the same allocation
delete a;
delete b;      // double free — b == a
```

### Improper Copy Semantics

```cpp
class Buffer {
    int* data_;
public:
    Buffer()  : data_(new int[100]) {}
    ~Buffer() { delete[] data_; }
    // No user-defined copy constructor!
};

Buffer buf1;
Buffer buf2 = buf1;   // default copy: buf2.data_ == buf1.data_
// At scope exit: ~Buffer() called twice on the same pointer
```

This is the classic violation of the **Rule of Three** (pre-C++11) or **Rule of Five** (C++11+). If you write a destructor that releases a resource, you must also write a copy constructor and copy assignment operator.

### Exception-Unsafe Code

```cpp
Resource* r = new Resource();
try {
    r->initialize();   // might throw
} catch (...) {
    delete r;          // fine
    throw;
}
delete r;              // BUG: double-delete if no exception was thrown
                       // and r was already deleted inside catch
```

## Detecting Double Free

### AddressSanitizer

```bash
g++ -fsanitize=address -g double_free.cpp -o double_free
./double_free
```

```
ERROR: AddressSanitizer: attempting double-free on 0x602000000010
    #0 in operator delete(void*) ...
    #1 in main double_free.cpp:4
previously allocated by thread T0 here:
    #1 in main double_free.cpp:1
```

### Valgrind

```bash
valgrind ./double_free
# ==...== Invalid free() / delete / delete[] / realloc()
# ==...==  Address 0x... is 0 bytes inside a block of size 4 free'd
```

## Heap Corruption Beyond Double Free

Double free is one category. Other heap corruption patterns include:

| Bug | Description |
|-----|-------------|
| Heap buffer overflow | Writing past the end of an allocation overwrites metadata of adjacent blocks |
| Underflow | Writing before the start of an allocation |
| Use-after-free write | Corrupting freed memory that the allocator uses as bookkeeping |
| Misaligned free | Passing an interior pointer to `delete` rather than the allocation base |

All share the same characteristic: the damage is invisible at the point of corruption and manifests as a crash or wrong result somewhere unrelated.

## Worked Example: Rule of Five Fix

```cpp
class SafeBuffer {
    int* data_;
    std::size_t n_;
public:
    explicit SafeBuffer(std::size_t n)
        : data_(new int[n]()), n_(n) {}

    // Copy constructor — deep copy
    SafeBuffer(const SafeBuffer& other)
        : data_(new int[other.n_]()), n_(other.n_) {
        std::copy(other.data_, other.data_ + n_, data_);
    }

    // Copy assignment — copy-and-swap idiom
    SafeBuffer& operator=(SafeBuffer other) {   // by value = copy
        std::swap(data_, other.data_);
        std::swap(n_, other.n_);
        return *this;
    }

    // Move constructor
    SafeBuffer(SafeBuffer&& other) noexcept
        : data_(other.data_), n_(other.n_) {
        other.data_ = nullptr; other.n_ = 0;
    }

    // Destructor
    ~SafeBuffer() { delete[] data_; }
};
```

Nulling `other.data_` in the move constructor ensures the moved-from destructor's `delete[] nullptr` is a safe no-op.

## Interview Answer

> **Q: How can a double-free bug be exploited by an attacker?**
>
> The attacker triggers the double-free to corrupt the allocator's free-list, then performs a controlled allocation that causes `malloc` to return a pointer overlapping a sensitive region (e.g., a function pointer table or security cookie); writing to that region gives the attacker code execution.
