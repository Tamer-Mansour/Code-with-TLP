# Pointer vs Reference: What Is the Difference?

Both pointers and references give indirect access to an object, but they differ in safety guarantees, syntax, and intended use. Knowing when to reach for each is a fundamental C++ design skill.

## Side-by-Side Comparison

| Feature | Pointer (`T*`) | Reference (`T&`) |
|---|---|---|
| Can be null | Yes (`nullptr`) | No — always bound |
| Can be reseated | Yes | No |
| Requires initialization | No | Yes |
| Dereference syntax | `*ptr`, `ptr->m` | Direct: `ref`, `ref.m` |
| Arithmetic allowed | Yes (`ptr + 1`) | No |
| Can point to array | Yes | No (single object) |
| Sizeof returns | Size of pointer | Size of referenced object |

## Syntax Differences

```cpp
int value = 42;

// Pointer
int* ptr = &value;
*ptr = 100;           // explicit dereference
std::cout << ptr;     // prints address
std::cout << *ptr;    // prints 100

// Reference
int& ref = value;
ref = 200;            // no dereference needed
std::cout << ref;     // prints 200 (the value)
```

## Nullability

A pointer can legally be `nullptr`, so every function accepting a pointer should check for null if it cannot guarantee a valid object will always be passed. A reference, by contrast, is guaranteed non-null at the language level — you never write a null-check for a reference parameter.

```cpp
void processPtr(int* p) {
    if (!p) return;   // must guard
    *p *= 2;
}

void processRef(int& r) {
    r *= 2;           // safe — r is always valid
}
```

> Note: It is technically possible to construct a dangling reference through undefined behavior (e.g., dereferencing a null pointer), but that is a program bug, not a valid language state.

## Reseating

A pointer can be redirected to a different object at any time. A reference is permanently bound at initialization:

```cpp
int a = 1, b = 2;

int* p = &a;
p = &b;       // p now points to b — legal

int& r = a;
r = b;        // this ASSIGNS b's value to a; r still refers to a
```

This is one of the most common misunderstandings: `r = b` does not rebind `r`.

## Pointer Arithmetic and Arrays

Pointers support arithmetic — this is essential for walking through raw arrays and implementing data structures. References do not:

```cpp
int arr[4] = {10, 20, 30, 40};
int* p = arr;
std::cout << *(p + 2); // 30

// References cannot index into an array this way
```

## When to Use Each

**Use a reference when:**
- The parameter is always required (never optional/null).
- You want clean, dereference-free syntax.
- Expressing an alias or output parameter cleanly.
- Returning from operator overloads (`operator[]`, `operator=`).

**Use a pointer when:**
- The argument is optional (can be `nullptr`).
- You need to iterate over a contiguous block (pointer arithmetic).
- You need to reseat mid-function (e.g., traversing a linked list node).
- Interfacing with C APIs that pass addresses.

## Worked Example: Optional vs Required Output

```cpp
// Pointer: caller may pass nullptr to skip out-value
bool divide(int a, int b, int* remainder) {
    if (b == 0) return false;
    if (remainder) *remainder = a % b;
    return true;
}

// Reference: caller must provide the out-value
int mustAdd(int a, int b, int& result) {
    result = a + b;
    return result;
}
```

## Common Pitfalls

- Returning a pointer or reference to a local variable — dangling access, undefined behavior.
- Treating assignment to a reference as reseating.
- Using pointers where references suffice — unnecessary complexity.
- Forgetting to null-check pointer parameters in library code.

> **Interview answer:** The key differences are nullability, reseating, and syntax. Pointers can be null and reseated; references cannot. Use references when the object is guaranteed to exist and reseating is not needed; use pointers when optionality or pointer arithmetic is required.
