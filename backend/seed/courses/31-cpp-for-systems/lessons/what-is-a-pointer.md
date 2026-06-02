# What Is a Pointer and How Does It Work?

A pointer is a variable that stores a **memory address** — the location of another variable in RAM. Instead of holding data directly, a pointer holds the address where data lives.

## Memory Addresses: The Core Idea

Every variable you declare occupies space in memory, and every byte in memory has a unique numeric address (typically written in hex). A pointer simply stores one of those addresses.

```cpp
int x = 42;
int* p = &x;   // p holds the address of x

std::cout << x << "\n";   // 42        — the value
std::cout << &x << "\n";  // 0x7ffd... — address of x
std::cout << p << "\n";   // 0x7ffd... — same address, stored in p
```

## Declaring a Pointer

The `*` in a declaration means "pointer to":

```cpp
int*    pi;   // pointer to int
double* pd;   // pointer to double
char*   pc;   // pointer to char (common for strings in C)
```

Pointer declarations bind to the variable name, not the type keyword — a common source of confusion:

```cpp
int* a, b;   // a is int*, but b is plain int!
int *a, *b;  // both are int* — this style makes it clearer
```

## Size of a Pointer

On a 64-bit system, **every pointer is 8 bytes** regardless of the type it points to — a pointer is just an address, and all addresses are the same width.

```cpp
std::cout << sizeof(int*)    << "\n";  // 8
std::cout << sizeof(double*) << "\n";  // 8
std::cout << sizeof(char*)   << "\n";  // 8
```

On a 32-bit system all pointers are 4 bytes. This matters when porting code.

## The Relationship Between Pointer and Pointee

A pointer and the variable it points to are separate entities:

| Variable | What it stores | Size (64-bit) |
|----------|---------------|---------------|
| `int x = 42` | the integer 42 | 4 bytes |
| `int* p = &x` | address of `x` | 8 bytes |

Changing `x` does not change `p` (the address stays the same). Changing `p` (making it point somewhere else) does not change `x`.

## Why Pointers Exist

Pointers solve real problems in systems programming:

- **Pass by reference**: functions can modify the caller's variable without copying large objects.
- **Dynamic memory**: `malloc` / `new` return a pointer to heap-allocated memory.
- **Arrays and strings in C**: arrays are accessed through pointers.
- **Function pointers**: store and call functions at runtime — the foundation of callbacks and vtables.
- **Low-level hardware access**: device drivers read/write specific memory-mapped addresses directly.

## A Worked Example

```cpp
#include <iostream>

void doubleIt(int* p) {
    *p = *p * 2;   // dereference p to reach the original variable
}

int main() {
    int value = 10;
    doubleIt(&value);             // pass the address of value
    std::cout << value << "\n";   // 20 — original was modified
}
```

Without pointers you would need to return the new value and reassign it at the call site. With a pointer the function writes directly to the caller's memory.

## Common Pitfalls

- **Uninitialized pointer**: reading or writing through a pointer that was never assigned causes undefined behavior.
- **Dangling pointer**: pointing to memory that has already been freed or has gone out of scope.
- **Confusing `*` in declaration vs. expression**: in `int* p` the `*` declares a type; in `*p = 5` the `*` dereferences.

> **Interview answer:** A pointer is a variable that stores the memory address of another variable. On a 64-bit system all pointers are 8 bytes. The key operations are taking an address with `&` and reading/writing through the pointer with `*` (dereference).
