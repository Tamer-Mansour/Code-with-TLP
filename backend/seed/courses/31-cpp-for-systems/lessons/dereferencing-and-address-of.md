# Dereference (*) and Address-of (&) Operators

These two operators are the fundamental tools for working with pointers. They are inverses of each other: `&` takes a variable and gives you its address; `*` takes an address and gives you what lives there.

## The Address-of Operator: `&`

When used in an **expression** (not a declaration), `&` returns the memory address of its operand.

```cpp
int x = 99;
int* p = &x;   // &x evaluates to the address where x lives
```

Rules:
- You can only take the address of an **lvalue** — something with a stable memory location (a named variable, array element, struct member).
- You cannot write `&42` or `&(a + b)` — temporaries have no address.

```cpp
int* bad = &(x + 1);  // ERROR: x+1 is a temporary, no address
```

## The Dereference Operator: `*`

In an expression, `*p` follows the pointer and accesses the value at the address stored in `p`. This is called **dereferencing**.

```cpp
int x = 99;
int* p = &x;

std::cout << *p << "\n";   // 99  — read through the pointer
*p = 200;                  // write through the pointer
std::cout << x << "\n";    // 200 — x itself was changed
```

The expression `*p` is an lvalue, so you can assign to it, take its address, or pass it by reference.

## Round-Trip Identity

`&` and `*` cancel each other out:

```cpp
int x = 5;
int* p = &x;

*(&x) == x;   // true — address then dereference = original
&(*p) == p;   // true — dereference then address = original pointer
```

## Reading Complex Declarations

The `*` in a **declaration** is different from the `*` in an **expression**:

```cpp
int* p;    // declaration: p is a pointer-to-int
*p = 10;   // expression: dereference p and write 10 there
```

This dual role confuses beginners. The rule: `*` in a declaration describes the **type** of the variable; `*` in an expression is an **operator**.

## Worked Example: Swap Without Returning a Value

```cpp
#include <iostream>

void swap(int* a, int* b) {
    int temp = *a;   // read the value a points to
    *a = *b;         // write b's value into a's location
    *b = temp;       // write saved value into b's location
}

int main() {
    int x = 1, y = 2;
    swap(&x, &y);
    std::cout << x << " " << y << "\n";  // 2 1
}
```

This is a classic interview warm-up. The function receives two addresses, not two values, so it can modify the originals directly.

## Structs and the Arrow Operator

When you have a pointer to a struct, dereferencing then using `.` is so common that C/C++ provide the `->` shorthand:

```cpp
struct Point { int x, y; };

Point pt = {3, 4};
Point* pp = &pt;

std::cout << (*pp).x << "\n";  // verbose — dereference then member access
std::cout << pp->x << "\n";    // identical, cleaner syntax
```

`pp->x` is exactly `(*pp).x`. Prefer `->` for pointer-to-struct access.

## Common Pitfalls

- **Dereferencing a null pointer**: `*nullptr` is undefined behavior and typically crashes.
- **Dereferencing an uninitialized pointer**: the pointer contains garbage; the access goes to a random memory location.
- **Forgetting `&` when calling**: if a function expects `int*`, passing `x` instead of `&x` is a type error (or implicit conversion gone wrong in C).

```cpp
void increment(int* p) { (*p)++; }

int n = 5;
increment(n);    // ERROR: n is int, not int*
increment(&n);   // correct
```

> **Interview answer:** `&x` returns the memory address of `x`. `*p` dereferences pointer `p`, giving access to the value stored at that address. They are inverse operations: `*(&x)` equals `x` and `&(*p)` equals `p`.
