# Function Overloading and Overload Resolution

Function overloading lets multiple functions share the same name as long as their **parameter lists** differ. The compiler picks the correct version at compile time — there is zero runtime cost.

## Rules for Valid Overloads

Two functions can coexist as overloads if their parameter types or counts differ after removing top-level `const` qualifiers and reference decorations that appear in the same position:

```cpp
void print(int x);          // overload 1
void print(double x);       // overload 2
void print(const char* s);  // overload 3
void print(int x, int y);   // overload 4 — different arity
```

These are **not** valid overloads because they differ only in return type (which the compiler cannot use to disambiguate a call):

```cpp
int  compute(int x);   // error: cannot overload on return type alone
void compute(int x);
```

Top-level `const` on a value parameter is also ignored (it does not create a new overload):

```cpp
void f(int x);         // same signature as f(const int x)
void f(const int x);   // redefinition, not overload
```

## How the Compiler Resolves Overloads

Resolution is a three-phase ranking:

1. **Exact match** — argument type matches parameter type directly (or with trivial array/function-to-pointer decay).
2. **Promotion** — integral types narrower than `int` (e.g., `char`, `short`) are promoted; `float` is promoted to `double`.
3. **Standard conversion** — numeric conversions, pointer conversions, boolean conversions.
4. **User-defined conversion** — constructors and conversion operators.
5. **Ellipsis `...`** — last resort.

If two overloads tie at the same rank the call is **ambiguous** and a compile error results.

```cpp
void f(int);
void f(double);

f(3);     // exact match: f(int)
f(3.0);   // exact match: f(double)
f(3.0f);  // float promoted to double -> f(double)
f('A');   // char promoted to int -> f(int)
```

## Ambiguity Example

```cpp
void g(int,    double);
void g(double, int);

g(1, 2);  // error: ambiguous — both require one conversion
```

## Name Mangling

The linker distinguishes overloads via **name mangling** — encoding the parameter types into the symbol name. In GCC/Clang, `print(int)` might become `_Z5printi`, while `print(double)` becomes `_Z5printd`.

```bash
# Demangle with c++filt:
nm prog | c++filt | grep print
```

`extern "C"` disables mangling (C linkage cannot be overloaded):

```cpp
extern "C" void c_api_func(int);  // single name, no overloads
```

## Overloading vs. Templates

- Use overloading when each type requires meaningfully different logic.
- Use function templates when the logic is identical for all types.

```cpp
// Overloading: different logic
void serialize(int x);
void serialize(float x);
void serialize(const char* s);

// Template: same logic, just different types
template<typename T>
T clamp(T val, T lo, T hi) { return val < lo ? lo : val > hi ? hi : val; }
```

## Worked Example: Logging Overloads

```cpp
#include <cstdio>
#include <cstring>

void log(int v)          { printf("[INT]    %d\n",   v); }
void log(double v)       { printf("[DOUBLE] %f\n",   v); }
void log(const char* s)  { printf("[STR]    %s\n",   s); }
void log(bool b)         { printf("[BOOL]   %s\n",   b ? "true" : "false"); }

int main() {
    log(42);
    log(3.14);
    log("hello");
    log(true);
    log(0);       // resolves to log(int) — not log(bool)!
}
```

**Output:**
```
[INT]    42
[DOUBLE] 3.140000
[STR]    hello
[BOOL]   true
[INT]    0
```

Note: `log(0)` resolves to `log(int)`, not `log(bool)`, because `int` is an exact match and `bool` would require a conversion. This surprises many developers.

## Pitfalls

- **Unexpected promotions** — `char` and `short` silently promote to `int`.
- **bool vs int ambiguity** — `0` and `1` prefer `int` over `bool`.
- **Pointer vs array** — array arguments decay to pointers; `const char[5]` matches `const char*`.
- **Too many overloads** — if every combination needs its own overload, consider a template or a different design.

> **Interview answer:** Overload resolution ranks candidates by conversion cost — exact match beats promotion beats standard conversion. The compiler picks the unique best candidate; a tie is a compile-time ambiguity error. Return type is never used for resolution.
