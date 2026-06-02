# Pass by Pointer: When and Why

Passing a pointer hands the function the *address* of the caller's object. The function can then read or write through that address, and the caller sees every change. It is the classic C idiom for "output parameters" and for optional arguments.

## Mechanics

```cpp
void increment(int* p) {
    if (!p) return;   // guard against null
    (*p)++;
}

int main() {
    int x = 10;
    increment(&x);    // pass address of x
    std::cout << x;   // 11
}
```

The caller explicitly takes the address with `&x`, which signals at the call site that `x` may be modified. This explicitness is one reason some coding guidelines prefer pointers over references for output parameters.

## When to Use Pass by Pointer

| Use case | Why pointer fits |
|---|---|
| Optional argument (may be `nullptr`) | Pointer can be null; reference cannot |
| Output parameter where call-site explicitness matters | `foo(&result)` signals mutation clearly |
| C-API interoperability | C has no references; raw pointers are required |
| Polymorphism on heap objects | Pointer to base class; virtual dispatch |
| Pointer arithmetic / array traversal | Pointers support `ptr + n`, `ptr++` |

## Optional Parameter Pattern

```cpp
bool parseNumber(const char* str, int* outValue) {
    // Returns false on failure; outValue is optional
    char* end;
    long v = std::strtol(str, &end, 10);
    if (end == str) return false;
    if (outValue) *outValue = static_cast<int>(v);
    return true;
}

int main() {
    int result;
    if (parseNumber("42", &result)) {
        std::cout << result;  // 42
    }
    parseNumber("bad", nullptr);  // caller ignores value — legal
}
```

## Pointer to Pointer: Output of a Pointer

For functions that must allocate and hand back a new object (common in C-style APIs), you pass a pointer-to-pointer:

```cpp
void createBuffer(char** buf, size_t size) {
    *buf = new char[size];
}

int main() {
    char* buffer = nullptr;
    createBuffer(&buffer, 256);
    // ... use buffer ...
    delete[] buffer;
}
```

## Common Pitfalls

- **Forgetting to null-check.** Dereferencing `nullptr` is undefined behavior and usually a crash. Always guard unless you have a documented contract that the pointer is never null.

```cpp
void bad(int* p) {
    *p = 5;   // crash if p == nullptr
}
```

- **Dangling pointer.** Storing the pointer and using it after the pointed-to object's lifetime ends is undefined behavior.

```cpp
int* danglingExample() {
    int local = 42;
    return &local;   // local is destroyed; pointer is dangling
}
```

- **Ownership ambiguity.** Raw pointers carry no ownership semantics. Document clearly whether the caller or callee is responsible for `delete`. Prefer `std::unique_ptr` / `std::shared_ptr` for owned heap objects in modern C++.

- **Confusing `*` in declaration vs expression.** `int* p` declares a pointer; `*p` in an expression dereferences it.

## Worked Example: In-Place Array Reverse

```cpp
#include <algorithm>

void reverseArray(int* arr, int n) {
    for (int i = 0, j = n - 1; i < j; ++i, --j) {
        std::swap(arr[i], arr[j]);
    }
}

int main() {
    int data[] = {1, 2, 3, 4, 5};
    reverseArray(data, 5);
    for (int v : data) std::cout << v << " "; // 5 4 3 2 1
}
```

`data` decays to a pointer; `reverseArray` walks it with index arithmetic.

## Pointer vs Reference for Output Parameters

Some teams choose references; others choose pointers. A widely cited rule:

- **Pointer** if the argument is optional or if call-site visibility of mutation matters.
- **Reference** if the argument is always required and you want cleaner syntax.

> **Interview answer:** Pass by pointer when the argument is optional (can be null), when interfacing with C APIs, when pointer arithmetic is needed, or when you want the call site to visibly signal mutation via `&`. Always null-check pointer parameters unless the contract guarantees a non-null value.
