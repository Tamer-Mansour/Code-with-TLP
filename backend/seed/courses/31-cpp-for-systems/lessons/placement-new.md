# Placement new and Manual Object Construction

## What Is Placement new?

Placement new is a variant of `new` that constructs an object at an address you supply — instead of asking the allocator for memory. The syntax places an extra argument (the target address) between `new` and the type:

```cpp
#include <new>     // required for placement new

char buf[sizeof(int)];            // pre-allocated storage
int* p = new (buf) int(42);       // construct in buf — no heap allocation
// p == (int*)buf

p->~int();  // destroy: trivial for int, but always call it for non-trivial types
```

No memory is allocated or freed by placement new itself. Destruction requires an **explicit destructor call** — you must never call `delete` on a placement-new'd pointer.

## The Three-Step Pattern

```
1. Acquire raw storage (stack buffer, heap, memory-mapped region, etc.)
2. Construct the object with placement new
3. Explicitly call the destructor; release storage with its original mechanism
```

```cpp
#include <new>
#include <cstdlib>
#include <cstring>

struct Sensor {
    int id;
    float value;
    Sensor(int i, float v) : id(i), value(v) {}
    ~Sensor() { /* release hardware handle if any */ }
};

int main() {
    // Step 1: allocate raw bytes (using malloc here for demonstration)
    void* raw = std::malloc(sizeof(Sensor));

    // Step 2: construct object in the raw storage
    Sensor* s = new (raw) Sensor(7, 3.14f);

    // Use the object normally
    s->value *= 2.0f;

    // Step 3: destroy, then free storage
    s->~Sensor();                // explicit destructor call
    std::free(raw);              // free the raw bytes
}
```

## Alignment Requirements

Storage provided to placement new must satisfy the type's alignment. Using a plain `char` array risks misalignment for types with stricter requirements:

```cpp
// Potentially misaligned — undefined behavior for double (alignment 8)
char bad[sizeof(double)];
double* d = new (bad) double(1.5);   // may be misaligned

// Correctly aligned using alignas or std::aligned_storage
alignas(double) char good[sizeof(double)];
double* d2 = new (good) double(1.5);  // guaranteed aligned
```

C++17 introduced `std::aligned_storage` and `std::byte` as cleaner alternatives to raw `char` arrays.

## Use Cases

### Object Pools

```cpp
struct Node { int val; Node* next; };

constexpr int POOL_SIZE = 1024;
alignas(Node) char pool[POOL_SIZE * sizeof(Node)];
int pool_top = 0;

Node* alloc_node(int v) {
    if (pool_top >= POOL_SIZE) return nullptr;
    Node* p = new (pool + pool_top * sizeof(Node)) Node{v, nullptr};
    ++pool_top;
    return p;
}
```

This eliminates per-object heap allocation overhead — critical in real-time or embedded systems.

### Custom Allocators

Standard library containers accept a custom `Allocator` template parameter. The allocator's `construct` method uses placement new to build the element inside allocator-managed memory.

### Kernel / Bare-Metal Code

Kernels cannot call `malloc`; they manage their own memory pages. Placement new lets them use C++ constructors on specific physical addresses:

```cpp
// Hypothetical kernel: map device register at known address
volatile DeviceRegs* regs = new ((void*)0xFED40000) DeviceRegs;
regs->~DeviceRegs();  // called during device teardown
```

## Common Mistakes

| Mistake | Consequence |
|---------|-------------|
| Calling `delete` on a placement-new pointer | UB — may corrupt a pool, crash, or double-free |
| Forgetting the explicit destructor call | Resource leaks (file handles, mutexes, etc.) |
| Misaligned storage | UB — trap on strict-alignment architectures |
| Overlapping constructions | UB — two live objects sharing the same bytes |

## Worked Example: In-Place Vector

```cpp
template<typename T, int N>
class InPlaceVec {
    alignas(T) char storage_[N * sizeof(T)];
    int size_ = 0;
public:
    void push_back(const T& val) {
        new (storage_ + size_ * sizeof(T)) T(val);
        ++size_;
    }
    ~InPlaceVec() {
        for (int i = size_ - 1; i >= 0; --i)
            reinterpret_cast<T*>(storage_ + i * sizeof(T))->~T();
    }
};
```

## Interview Answer

> **Q: When would you use placement new instead of ordinary `new`?**
>
> When you need to control exactly where an object lives — such as a pre-allocated memory pool, a specific physical address in a kernel, or a shared-memory region — placement new lets you invoke the constructor at that address without performing any allocation.
