# const int*, int* const, const int* const Explained

This is one of the most common C++ interview questions. Three similar-looking declarations mean three very different things. Master the reading rule once and you will never confuse them again.

## The Reading Rule: "Read Right to Left"

Start from the variable name and read rightward, then loop back through what is left of the `*`.

| Declaration | Read as |
|-------------|---------|
| `const int* p` | `p` is a pointer to `int` that is `const` |
| `int* const p` | `p` is a `const` pointer to `int` |
| `const int* const p` | `p` is a `const` pointer to `const int` |

An easier mnemonic: **whatever appears to the right of `*` is const** — so if `const` is to the right of `*` the pointer itself is const; if `const` is to the left of `*` the data is const.

## Case 1: `const int* p` — Pointer to Const Data

The pointer can be reseated (changed to point elsewhere). The data it points to cannot be modified through this pointer.

```cpp
int x = 10, y = 20;
const int* p = &x;

// *p = 99;   // ERROR: data is const through this pointer
p = &y;       // OK: p itself can change
std::cout << *p << "\n";  // 20
```

Also written as `int const* p` — both mean the same thing (const is to the left of `*`).

**Use case**: passing a read-only view of data to a function.

```cpp
void print(const int* data, int n) {
    for (int i = 0; i < n; i++)
        std::cout << data[i] << " ";
}
```

## Case 2: `int* const p` — Const Pointer to Mutable Data

The pointer is fixed (cannot be reseated). The data it points to can be modified through the pointer.

```cpp
int x = 10, y = 20;
int* const p = &x;   // p is locked to &x forever

*p = 99;    // OK: modifying the data is fine
// p = &y;  // ERROR: p cannot be reseated
std::cout << x << "\n";  // 99
```

**Use case**: a reference-like handle — you know the pointer will never change target, similar to a reference variable.

## Case 3: `const int* const p` — Const Pointer to Const Data

Both the pointer itself and the data are immutable. Nothing about this pointer can be changed.

```cpp
int x = 42;
const int* const p = &x;

// *p = 99;  // ERROR: data is const
// p = ...;  // ERROR: pointer is const
std::cout << *p << "\n";  // 42
```

**Use case**: a compile-time-guaranteed immutable view. Common in low-level drivers where a memory-mapped register address never changes and must not be written to.

## Side-by-Side Comparison

```cpp
int a = 1, b = 2;

const int* p1 = &a;   // pointer to const int
p1 = &b;              // OK
// *p1 = 9;           // ERROR

int* const p2 = &a;   // const pointer to int
*p2 = 9;              // OK — a is now 9
// p2 = &b;           // ERROR

const int* const p3 = &a;  // const pointer to const int
// *p3 = 9;                // ERROR
// p3 = &b;                // ERROR
std::cout << *p3 << "\n";  // 9 (reading is always allowed)
```

## The `cdecl` Rule for Complex Types

For any declaration, apply this recipe:

1. Find the variable name.
2. Go right until `)` or end-of-line.
3. Go left past any `*`.
4. Repeat from step 2 until done.

For `const int* const p`: start at `p`, go right → end; go left → `const` (pointer is const), then `*` (it's a pointer), then `int` (points to int), then `const` (int is const). Result: "const pointer to const int".

## Function Parameters: Practical Usage

```cpp
// Read-only access to array — const int* is idiomatic
void inspect(const int* arr, int n);

// Will modify elements but not reseat the pointer — rare but explicit
void fill(int* const arr, int n, int val) {
    for (int i = 0; i < n; i++) arr[i] = val;
}

// Return a read-only pointer from a getter
const char* getName() const;
```

## Common Pitfalls

- **Dropping const (const-casting away)**: assigning `const int*` to `int*` is a compile error. Using `const_cast` to remove const and then writing is undefined behavior if the original object was truly const.
- **Confusing the two simpler forms**: a quick memory aid — "if `const` comes before `*`, data is const; if `const` comes after `*`, pointer is const."

> **Interview answer:** `const int*` is a pointer to read-only data (pointer can change, data cannot). `int* const` is a read-only pointer to mutable data (pointer fixed, data can change). `const int* const` locks both. The rule: `const` to the left of `*` constrains the data; `const` to the right of `*` constrains the pointer.
