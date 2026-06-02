# new[] and delete[]: Why Mismatch Is UB

## Array Allocation in C++

When you allocate an array with `new[]`, the runtime does more than multiply element count by element size. It typically stores metadata — most commonly the element count — in a hidden header just before the returned pointer. `delete[]` reads that count to know how many destructors to call.

```cpp
#include <iostream>

struct Noisy {
    int val;
    Noisy() : val(0)  { std::cout << "ctor\n"; }
    ~Noisy()          { std::cout << "dtor\n"; }
};

int main() {
    Noisy* arr = new Noisy[3];   // 3 constructors called
    // ... use arr[0], arr[1], arr[2] ...
    delete[] arr;                // 3 destructors called, in reverse order
}
```

Output:
```
ctor
ctor
ctor
dtor
dtor
dtor
```

## The Hidden Cookie

Most implementations prepend an overhead block (sometimes called the "array cookie") storing the element count:

```
Heap layout (conceptual):
[ cookie: 3 ][ Noisy[0] ][ Noisy[1] ][ Noisy[2] ]
              ^
              pointer returned to you
```

`delete[]` walks back by a fixed offset to find the cookie, reads `3`, calls three destructors, then frees the block including the cookie.

## What Happens on Mismatch

### Using `delete` on an Array Pointer

```cpp
Noisy* arr = new Noisy[3];
delete arr;   // UNDEFINED BEHAVIOR
```

- Only the destructor for `arr[0]` is called.
- The runtime frees memory using the pointer that was returned — but the allocation included the cookie header, so the bookkeeping is wrong.
- In practice: one destructor, heap corruption, or crash at a later allocation.

### Using `delete[]` on a Single-Object Pointer

```cpp
Noisy* obj = new Noisy;
delete[] obj;   // UNDEFINED BEHAVIOR
```

- The runtime reads a "count" from before the pointer — but no cookie was written there. It reads arbitrary memory as a count and calls that many (bogus) destructors.
- Almost certainly a crash or silent memory corruption.

## Primitive Types: Why You Must Still Match

For types without destructors (like `int`), some compilers happen to skip the cookie, making the mismatch "appear" harmless. This is purely an implementation accident:

```cpp
int* arr = new int[10];
delete arr;    // UB — even if it "works" today, it is not guaranteed
```

The C++ standard makes no exception. Relying on it being harmless leads to non-portable, fragile code.

## Rules to Memorize

| Allocation | Required Deallocation |
|------------|-----------------------|
| `new T` | `delete` |
| `new T[n]` | `delete[]` |
| `new (buf) T` | `~T()` explicitly (no delete) |
| `malloc` | `free` |

## Worked Example: Fixed-Size Arena

```cpp
constexpr int N = 100;

class Arena {
    char* storage_;
public:
    Arena()  : storage_(new char[N * sizeof(double)]()) {}
    ~Arena() { delete[] storage_; }   // must be delete[], not delete

    double* at(int i) {
        return reinterpret_cast<double*>(storage_) + i;
    }
};
```

If the destructor used plain `delete` instead of `delete[]`, the behavior would be undefined. Static analysis tools and sanitizers (AddressSanitizer, Valgrind) will catch this mismatch.

## Detecting Mismatches

```bash
# AddressSanitizer catches new/delete[] mismatches at runtime
g++ -fsanitize=address,undefined -g mismatch.cpp -o mismatch
./mismatch
# ERROR: AddressSanitizer: alloc-dealloc-mismatch (new vs delete []) ...
```

## Interview Answer

> **Q: Why is calling `delete` instead of `delete[]` on an array undefined behavior?**
>
> `delete[]` relies on a hidden element count stored before the allocation to know how many destructors to call; plain `delete` does not read that count, so only one destructor runs and the heap bookkeeping is corrupted.
