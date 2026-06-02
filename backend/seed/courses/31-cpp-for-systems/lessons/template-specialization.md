# Template Specialization and Partial Specialization

The generic template definition works for most types, but sometimes a specific type (or category of types) needs a fundamentally different implementation. **Template specialization** lets you provide an alternate definition for particular template arguments.

## Full (Explicit) Specialization

A full specialization pins down all template parameters:

```cpp
// Primary template
template <typename T>
struct TypeName {
    static const char* get() { return "unknown"; }
};

// Full specialization for int
template <>
struct TypeName<int> {
    static const char* get() { return "int"; }
};

// Full specialization for double
template <>
struct TypeName<double> {
    static const char* get() { return "double"; }
};

TypeName<int>::get();    // "int"
TypeName<float>::get();  // "unknown"  — falls through to primary
```

The `template <>` header with an empty parameter list signals a full specialization.

## Function Template Specialization (and Its Pitfall)

Function templates can also be fully specialized, but it is usually better to use **overloading** instead:

```cpp
// Primary
template <typename T>
T zero() { return T{}; }

// Full specialization — legal but avoid
template <>
const char* zero<const char*>() { return ""; }

// Better: overload (not a template at all)
const char* zero_str() { return ""; }
```

The issue with function template specialization is that it does not participate in overload resolution the same way as overloads — this leads to surprising behavior. Prefer overloading or `if constexpr` for function-level customization.

## Partial Specialization (Class Templates Only)

Partial specialization fixes some parameters while leaving others open. It is only available for **class templates**, not function templates.

```cpp
// Primary
template <typename T, typename U>
struct Pair {
    static void describe() { std::cout << "generic pair\n"; }
};

// Partial specialization: both types are the same
template <typename T>
struct Pair<T, T> {
    static void describe() { std::cout << "same-type pair\n"; }
};

// Partial specialization: second type is a pointer
template <typename T, typename U>
struct Pair<T, U*> {
    static void describe() { std::cout << "pair with pointer second\n"; }
};

Pair<int, double>::describe();   // "generic pair"
Pair<int, int>::describe();      // "same-type pair"
Pair<int, int*>::describe();     // "pair with pointer second"
```

The compiler picks the **most specialized** matching specialization. Ambiguous matches are a compile error.

## Specializing for Pointer Types

A classic use: provide a more efficient or different implementation for pointer types.

```cpp
template <typename T>
class Storage {
    T data_;
public:
    void set(T v) { data_ = v; }
    T    get() const { return data_; }
};

// Partial specialization: T is a pointer
template <typename T>
class Storage<T*> {
    T* data_;
public:
    void set(T* p) { data_ = p; }
    T*   get() const { return data_; }
    T    deref() const { return *data_; }   // extra operation only for pointers
};

Storage<int>  s1; s1.set(42);
Storage<int*> s2; int x = 7; s2.set(&x);
int y = s2.deref();  // 7
```

## Type Traits Are Built on Specialization

The standard `<type_traits>` library is built almost entirely on partial specialization:

```cpp
// Simplified std::is_pointer
template <typename T>
struct is_pointer { static constexpr bool value = false; };

template <typename T>
struct is_pointer<T*> { static constexpr bool value = true; };

static_assert(!is_pointer<int>::value);
static_assert( is_pointer<int*>::value);
```

## Worked Example: Serializer

```cpp
#include <cstdint>
#include <cstring>
#include <vector>

template <typename T>
struct Serializer {
    static void write(std::vector<uint8_t>& buf, const T& val) {
        const auto* p = reinterpret_cast<const uint8_t*>(&val);
        buf.insert(buf.end(), p, p + sizeof(T));
    }
};

// Specialization for bool: store as a single byte 0 or 1
template <>
struct Serializer<bool> {
    static void write(std::vector<uint8_t>& buf, bool val) {
        buf.push_back(val ? 1u : 0u);
    }
};
```

## Specialization Resolution Order

When the compiler looks up a template instantiation it:

1. Finds all matching specializations (primary + partials + full).
2. Selects the **most specific** one.
3. If two partial specializations are equally good, it is ambiguous — compile error.

## Common Pitfalls

- Partial specialization of **function templates** is illegal — use overloading instead.
- A full specialization must appear **after** the primary template declaration and **before** first use.
- Over-specializing creates hidden behavior: callers do not expect `Container<bool>` to behave differently from `Container<int>` unless documented.

> **Interview answer:** "Full specialization provides a completely separate implementation for one specific set of template arguments. Partial specialization matches a pattern over some arguments, used heavily in type traits. Function templates cannot be partially specialized — use overloading or `if constexpr` instead."
