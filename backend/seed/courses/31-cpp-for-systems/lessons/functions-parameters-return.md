# Functions: Parameters, Return Values, and Scope

Functions are the primary unit of abstraction in C++. Understanding how arguments are passed, how values are returned, and how names are resolved is critical for writing correct, efficient systems code.

## Parameter Passing Modes

C++ passes arguments by value by default. The function gets a **copy**.

```cpp
void increment(int x) { x += 1; }  // caller's variable unchanged
```

### Pass by reference

A reference is an alias — no copy, no pointer syntax at the call site:

```cpp
void increment(int& x) { x += 1; }  // modifies caller's variable

int n = 5;
increment(n);  // n is now 6
```

### Pass by const reference

For large or non-trivial types, use `const&` to avoid copying while preventing modification:

```cpp
void print_name(const std::string& s) { puts(s.c_str()); }
```

### Pass by pointer

Use a pointer when `nullptr` is a meaningful value (optional argument) or when C interoperability is required:

```cpp
bool find(const int* arr, int n, int target, int* out_index) {
    for (int i = 0; i < n; ++i)
        if (arr[i] == target) { *out_index = i; return true; }
    return false;
}
```

| Mode | Syntax | Copies? | Can modify caller? | Nullable? |
|---|---|---|---|---|
| By value | `T x` | Yes | No | N/A |
| By reference | `T& x` | No | Yes | No |
| By const ref | `const T& x` | No | No | No |
| By pointer | `T* x` | No (ptr only) | Yes (via `*`) | Yes |

## Return Values

A function with a non-void return type **must** return on all control paths (undefined behavior otherwise):

```cpp
int sign(int x) {
    if (x > 0) return  1;
    if (x < 0) return -1;
    return 0;          // must not forget this
}
```

### Returning multiple values

C++ lacks built-in multiple returns; common idioms:

```cpp
// 1. Output parameters (pointer or reference)
bool parse_int(const char* s, int* out);

// 2. std::pair or std::tuple
std::pair<bool, int> parse_int(const char* s);

// 3. Struct (most readable for 3+ values)
struct ParseResult { bool ok; int value; };
ParseResult parse_int(const char* s);
```

### Return value optimization (RVO / NRVO)

The compiler typically constructs the return value directly in the caller's storage, eliding the copy even for large objects. You can rely on this in practice — do not pessimize by returning `std::move(local)` unnecessarily.

## Scope

- **Local variables** live from their declaration to the end of the enclosing block `{}`.
- **Parameters** have the same lifetime as local variables in the function body.
- **Returning a pointer or reference to a local variable** is undefined behavior — the storage is gone when the function returns.

```cpp
int* danger() {
    int local = 42;
    return &local;   // UB: dangling pointer
}
```

### Static local variables

A `static` local is initialized once (on first call) and lives for the program's lifetime:

```cpp
int next_id() {
    static int id = 0;
    return ++id;
}
```

This is thread-safe for initialization since C++11 (the standard mandates it), but updates still need synchronization in multithreaded code.

## Worked Example: Safe Integer Division

```cpp
#include <cstdio>
#include <cerrno>

// Returns true on success, sets *result; on failure sets errno and returns false
bool safe_div(int numerator, int denominator, int* result) {
    if (denominator == 0) { errno = EDOM; return false; }
    *result = numerator / denominator;
    return true;
}

int main() {
    int val;
    if (safe_div(10, 3, &val))
        printf("10/3 = %d\n", val);

    if (!safe_div(5, 0, &val))
        perror("division");
}
```

**Output:**
```
10/3 = 3
division: Numerical argument out of domain
```

> **Interview answer:** C++ defaults to pass-by-value (copy). Use `const T&` for read-only access to large objects, `T&` for output parameters, and `T*` when the argument is optional/nullable. Never return a pointer or reference to a local variable — it becomes a dangling reference the moment the function returns.
