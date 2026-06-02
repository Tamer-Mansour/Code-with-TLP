# Arrays, Pointer Decay, and Array Indexing

Arrays and pointers are closely related in C and C++, but they are not the same thing. Understanding **pointer decay** — the implicit conversion from array to pointer — explains many behaviors that trip up intermediate programmers.

## What Is Pointer Decay?

When you use an array name in most expressions, it implicitly converts to a pointer to its first element. The array "decays" into a pointer, losing its size information.

```cpp
int arr[5] = {1, 2, 3, 4, 5};

int* p = arr;   // decay: arr → &arr[0]
```

The pointer `p` and the array `arr` are different types:

```cpp
std::cout << sizeof(arr) << "\n";  // 20 (5 × 4 bytes — full array)
std::cout << sizeof(p)   << "\n";  // 8  (pointer size — lost size info!)
```

This is why C functions that receive arrays must take a separate `int n` parameter — the size is lost at the call site.

## When Decay Does NOT Happen

Three contexts where an array does **not** decay to a pointer:

1. **`sizeof`** — returns the full array size, not pointer size.
2. **`&arr`** — takes the address of the entire array; type is `int(*)[5]`, not `int*`.
3. **Aggregate initialization** — `int b[] = arr;` is illegal; arrays cannot be copied with `=`.

```cpp
int arr[5] = {1, 2, 3, 4, 5};
int (*pa)[5] = &arr;   // pointer to the whole array
std::cout << sizeof(*pa) << "\n";  // 20 — still knows it's 5 ints
```

## Indexing Through Decay

Array indexing `arr[i]` is defined as `*(arr + i)`. After decay, both forms are equivalent:

```cpp
int arr[] = {10, 20, 30};
int* p    = arr;

arr[2]     == *(arr + 2)  // both 30
p[2]       == *(p + 2)    // both 30
arr[2]     == p[2]        // true
```

The compiler generates identical machine code for `arr[i]` and `*(arr + i)`.

## Passing Arrays to Functions

Because arrays decay, a function receiving `int arr[]` actually receives `int*`:

```cpp
// These three declarations are identical:
void sum(int arr[], int n);
void sum(int* arr,  int n);   // exactly the same as above
void sum(int arr[10], int n); // size hint ignored — still int*
```

This is why `sizeof(arr)` inside the function gives the pointer size, not the array size.

```cpp
void bad(int arr[]) {
    // sizeof(arr) == 8 here (pointer), not 20
    int n = sizeof(arr) / sizeof(arr[0]);  // WRONG: gives 2 on 64-bit
}
```

To preserve size, pass a pointer-to-array or use a template:

```cpp
template <int N>
void correct(int (&arr)[N]) {
    std::cout << N << "\n";   // knows the size at compile time
}
```

## Multidimensional Arrays

For 2D arrays, only the outermost dimension decays. A `int grid[3][4]` decays to `int(*)[4]` — a pointer to an array of 4 ints.

```cpp
int grid[3][4] = {};

int (*row)[4] = grid;   // pointer to one row (4 ints)
row[1][2] = 99;         // second row, third column
```

When passing a 2D array to a function, all but the first dimension must be specified:

```cpp
void process(int arr[][4], int rows);  // OK
void process(int arr[][], int rows);   // ERROR: inner size unknown
```

## Worked Example: Computing Array Stats Without Size Loss

```cpp
#include <iostream>

// Pass by reference-to-array: no decay, size preserved
template <int N>
double average(const int (&arr)[N]) {
    int sum = 0;
    for (int v : arr) sum += v;
    return (double)sum / N;
}

int main() {
    int scores[] = {88, 92, 75, 100, 85};
    std::cout << average(scores) << "\n";  // 88
}
```

## Common Pitfalls

- **`sizeof` inside a function**: always measures the pointer, not the original array.
- **Returning a local array**: local arrays decay to a dangling pointer when the function returns — undefined behavior.
- **Treating 2D array pointer arithmetic**: `arr + 1` on a `int arr[3][4]` moves forward by one full row (16 bytes), not 4 bytes.

```cpp
int arr[3][4] = {};
int* wrong = (int*)arr;
wrong++;            // +4 bytes — moves to arr[0][1]
int (*right)[4] = arr;
right++;            // +16 bytes — moves to arr[1][0]
```

> **Interview answer:** An array name decays to a pointer to its first element in most expressions, losing size information. `sizeof` is an exception — it still returns the full array size. This is why functions receiving arrays must take a separate length parameter or use a template reference-to-array to preserve the size.
