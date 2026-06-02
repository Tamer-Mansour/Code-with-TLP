# new and delete: Allocation with Construction

## What Makes `new` Different

In C++, `new` is not merely a memory allocator — it is an operator that combines two distinct actions: allocating raw memory from the heap and calling the constructor of the object being created. Symmetrically, `delete` calls the destructor and then releases the memory. This coupling is what separates C++ from C's manual approach.

```cpp
#include <iostream>

struct Point {
    double x, y;
    Point(double x, double y) : x(x), y(y) {
        std::cout << "Point constructed\n";
    }
    ~Point() {
        std::cout << "Point destroyed\n";
    }
};

int main() {
    Point* p = new Point(3.0, 4.0);  // allocates + constructs
    std::cout << p->x << ", " << p->y << "\n";
    delete p;                         // destructs + deallocates
}
```

Output:
```
Point constructed
3, 4
Point destroyed
```

## The Two-Phase Model

| Phase | `new` | `delete` |
|-------|-------|----------|
| Memory | `operator new` acquires raw bytes | `operator delete` releases raw bytes |
| Object | Constructor runs at the address | Destructor runs before release |

Understanding this split is crucial for advanced patterns like placement new, custom allocators, and object pooling.

## Default Initialization vs Value Initialization

```cpp
int* a = new int;    // default-initialized: value is indeterminate
int* b = new int();  // value-initialized: set to 0
int* c = new int(5); // direct-initialized: set to 5
```

Always prefer explicit initialization. Reading an indeterminate value is undefined behavior (UB).

## What Happens When Allocation Fails

By default, `new` throws `std::bad_alloc` if the system cannot satisfy the request. The destructor of any already-constructed sub-objects is called automatically before the exception propagates.

```cpp
#include <new>
try {
    int* big = new int[1'000'000'000'000LL]; // likely throws
} catch (const std::bad_alloc& e) {
    std::cerr << "Allocation failed: " << e.what() << "\n";
}
```

## Common Pitfalls

- **Forgetting `delete`** — every `new` must have exactly one matching `delete`; otherwise memory leaks.
- **Deleting a null pointer** — safe and a no-op; `delete nullptr` is guaranteed harmless.
- **Mismatching operators** — using `delete[]` on a single-object pointer or `delete` on an array pointer is undefined behavior.
- **Double delete** — calling `delete` twice on the same pointer corrupts the heap.

```cpp
int* p = nullptr;
delete p;   // harmless — always safe to delete nullptr
```

## Worked Example: Resource-Owning Class

```cpp
class Buffer {
    char* data_;
    std::size_t size_;
public:
    explicit Buffer(std::size_t n)
        : data_(new char[n]()), size_(n) {}   // value-init to 0

    ~Buffer() { delete[] data_; }             // must use delete[]

    char& operator[](std::size_t i) { return data_[i]; }
    std::size_t size() const { return size_; }
};
```

This pattern — acquiring in the constructor, releasing in the destructor — is the foundation of RAII (Resource Acquisition Is Initialization), the idiomatic C++ way to avoid leaks.

## Interview Answer

> **Q: What does `new` do that `malloc` does not?**
>
> `new` calls the constructor after allocating memory, and `delete` calls the destructor before freeing it; `malloc`/`free` only manage raw bytes with no knowledge of object lifetimes.
