# void Pointers and Function Pointers

Two specialized pointer types that appear constantly in C APIs and systems code: `void*` for type-erased memory, and function pointers for runtime-selectable behavior.

## void Pointers

A `void*` is a pointer to memory of unknown type. It can hold the address of any object, but you cannot dereference it or do arithmetic on it without first casting to a concrete type.

```cpp
int    x  = 42;
double d  = 3.14;

void* vp = &x;    // point at an int
vp       = &d;    // now point at a double — no cast needed to assign

// *vp = 10;      // ERROR: cannot dereference void*
// vp++;          // ERROR: no element size known

int* ip = (int*)vp;   // must cast before use
// or in C++:
int* ip2 = static_cast<int*>(vp);
std::cout << *ip2 << "\n";  // 42 if vp currently points at an int
```

### Where void* Is Used

- `malloc` / `calloc` return `void*` — cast to the target type on use.
- `memcpy`, `memset`, `qsort` accept `void*` so they work with any data type.
- C-style plugin/callback systems pass user data as `void*` ("context pointer").

```c
// Classic C: sorting integers with qsort
int cmp(const void* a, const void* b) {
    int ia = *(const int*)a;
    int ib = *(const int*)b;
    return (ia > ib) - (ia < ib);
}

int arr[] = {5, 2, 8, 1};
qsort(arr, 4, sizeof(int), cmp);
```

In C++ prefer typed alternatives (`std::sort`, templates, `std::any`) over `void*` when possible.

## Function Pointers

A function pointer stores the address of a function and lets you call it indirectly. The type encodes the function's signature exactly.

### Declaration Syntax

```cpp
// Syntax: return_type (*name)(param_types)
int (*fp)(int, int);   // pointer to a function taking two ints, returning int
```

The parentheses around `*name` are required — without them `int *fp(int, int)` declares a function that returns `int*`.

### Basic Usage

```cpp
#include <iostream>

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

int main() {
    int (*op)(int, int);   // declare

    op = add;              // assign — no & needed for functions
    std::cout << op(3, 4) << "\n";  // 7

    op = mul;
    std::cout << op(3, 4) << "\n";  // 12
}
```

### Using typedef / using for Readability

```cpp
using BinaryOp = int(*)(int, int);   // C++11 alias

BinaryOp ops[] = { add, mul };
std::cout << ops[0](5, 2) << "\n";   // 7
std::cout << ops[1](5, 2) << "\n";   // 10
```

### Functions as Arguments (Callbacks)

```cpp
void apply(int* arr, int n, int(*transform)(int)) {
    for (int i = 0; i < n; i++)
        arr[i] = transform(arr[i]);
}

int square(int x) { return x * x; }

int main() {
    int a[] = {1, 2, 3, 4, 5};
    apply(a, 5, square);
    for (int v : a) std::cout << v << " ";
    // 1 4 9 16 25
}
```

This pattern is the foundation of `qsort`, signal handlers, and OS callbacks.

## Comparing void* and Function Pointers

| Feature | `void*` | Function pointer |
|---------|---------|-----------------|
| Stores | address of data | address of code |
| Dereferenceable | no (must cast first) | yes (call it) |
| Arithmetic | not allowed | not allowed |
| C standard cast | `(T*)vp` | `(RetType(*)(Args))fp` |
| C++ cast | `static_cast<T*>` | `reinterpret_cast` (if needed) |

Note: the C standard does not guarantee that a `void*` can hold a function pointer — they are different kinds of pointers. On POSIX systems `dlsym` returns `void*` for functions, requiring a `reinterpret_cast`.

## Modern C++ Alternatives

- `std::function<Ret(Args...)>` — type-erased callable that works with lambdas, member functions, and functors.
- Templates — zero-cost alternative for compile-time polymorphism.
- `std::any` / `std::variant` — type-safe alternatives to `void*` for data.

Function pointers remain essential for C interop, OS APIs, and performance-critical paths (vtables use them internally).

## Common Pitfalls

- **Calling a null function pointer** — crashes immediately (undefined behavior).
- **Signature mismatch** — casting a function pointer to a different signature and calling it is UB, even if it "works" on a given ABI.
- **Member function pointers are different** — `int (MyClass::*mfp)(int)` requires an object instance to call and has different syntax from plain function pointers.

> **Interview answer:** `void*` is a type-erased data pointer used by generic C APIs; it must be cast before dereferencing. A function pointer stores a function's address and allows indirect calls; its type must match the function's signature exactly. Both exist in systems code; modern C++ provides safer typed alternatives for most use cases.
