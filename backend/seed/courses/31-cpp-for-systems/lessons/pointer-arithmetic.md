# Pointer Arithmetic and Why Type Size Matters

Pointers are not plain integers — adding 1 to a pointer moves it forward by **one element of the pointed-to type**, not by one byte. This is pointer arithmetic, and it is the mechanism behind array traversal in C and C++.

## The Core Rule

```
new_address = old_address + (n × sizeof(*pointer))
```

When you write `p + n`, the compiler multiplies `n` by `sizeof` of the element type and adds the result in bytes to the raw address.

```cpp
int arr[] = {10, 20, 30, 40};
int* p = arr;          // p points to arr[0], say address 0x1000

std::cout << p   << "\n";  // 0x1000
std::cout << p+1 << "\n";  // 0x1004  (+4 bytes, sizeof(int) = 4)
std::cout << p+2 << "\n";  // 0x1008
std::cout << p+3 << "\n";  // 0x100C
```

For `double*` (8 bytes each), `p+1` would jump 8 bytes. The type encodes the stride.

## Supported Operations

| Operation | Meaning |
|-----------|---------|
| `p + n` | address n elements ahead |
| `p - n` | address n elements behind |
| `p++` / `++p` | advance one element forward |
| `p--` / `--p` | step one element back |
| `p2 - p1` | number of elements between two pointers (same array) |
| `p[n]` | same as `*(p + n)` |

Subtraction of two pointers of the same type yields a `ptrdiff_t` — a signed integer representing the element distance, not the byte distance.

```cpp
int arr[] = {1, 2, 3, 4, 5};
int* start = &arr[0];
int* end   = &arr[4];
ptrdiff_t dist = end - start;   // 4 (not 16)
```

## Traversing an Array with Pointer Arithmetic

```cpp
#include <iostream>

int main() {
    int nums[] = {5, 10, 15, 20, 25};
    int n = sizeof(nums) / sizeof(nums[0]);  // 5

    for (int* p = nums; p < nums + n; ++p) {
        std::cout << *p << " ";
    }
    // output: 5 10 15 20 25
}
```

This is exactly what range-based for loops and iterators do internally.

## Indexing Is Arithmetic

`arr[i]` is 100% equivalent to `*(arr + i)`, and the compiler generates identical code. This also means `i[arr]` is technically legal C/C++ (addition is commutative), but never write it in production code.

```cpp
int a[] = {7, 8, 9};
std::cout << a[2]     << "\n";  // 9
std::cout << *(a + 2) << "\n";  // 9 — identical
std::cout << 2[a]     << "\n";  // 9 — legal but bizarre
```

## Why Type Size Matters: A Concrete Example

```cpp
int   iarr[] = {1, 2, 3};
char  carr[] = {1, 2, 3};

int*  ip = iarr;
char* cp = carr;

// Advancing by 1 element
ip++;   // moves forward 4 bytes (sizeof int = 4)
cp++;   // moves forward 1 byte  (sizeof char = 1)
```

If you accidentally cast an `int*` to a `char*` and do arithmetic, you get byte-level access — useful for serialization, dangerous if unintentional.

## Out-of-Bounds: Undefined Behavior

Pointer arithmetic is only defined within the bounds of an array (and one-past-the-end for comparisons). Going beyond produces undefined behavior — the program may crash, corrupt data, or appear to work on one platform and fail on another.

```cpp
int arr[3] = {1, 2, 3};
int* p = arr + 5;   // already undefined!
*p = 99;            // UB — memory corruption
```

## Differences from Integer Arithmetic

- `p + p` is **not allowed** — adding two pointers makes no sense.
- `p * 2` is **not allowed**.
- Only `+`, `-`, `++`, and `--` (and the derived `p[n]`) are valid on pointers.

## Common Pitfalls

- **Off-by-one**: iterating with `p <= arr + n` instead of `p < arr + n` reads one past the array.
- **Wrong type cast**: casting `int*` to `short*` and doing arithmetic gives wrong strides.
- **Forgetting stride when manually computing offsets** in 2D arrays or struct arrays.

> **Interview answer:** Adding `n` to a pointer of type `T*` moves the address forward by `n × sizeof(T)` bytes, not `n` bytes. This is why the element type of a pointer matters for arithmetic — it encodes the stride.
