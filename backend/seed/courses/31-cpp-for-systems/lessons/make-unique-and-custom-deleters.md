# make_unique and Custom Deleters

Two features round out practical `unique_ptr` usage: `std::make_unique` (the preferred construction idiom) and custom deleters (the escape hatch for non-`delete` cleanup).

## Why make_unique Exists

Before C++14, you had to write:

```cpp
std::unique_ptr<Widget> w(new Widget(arg1, arg2));
```

This is problematic in certain argument evaluation contexts. Consider:

```cpp
// Pre-C++14 danger
f(std::unique_ptr<Widget>(new Widget()), compute_value());
```

The compiler is allowed to evaluate these three sub-expressions in any order:
1. `new Widget()`
2. `compute_value()`
3. Construct `unique_ptr`

If step 1 succeeds, step 2 throws, and step 3 has not run yet — the `Widget` leaks. `std::make_unique` fixes this by fusing steps 1 and 3:

```cpp
f(std::make_unique<Widget>(), compute_value());  // safe
```

Now `new Widget()` and the `unique_ptr` construction are a single indivisible operation.

## make_unique Syntax

```cpp
// Single object
auto w = std::make_unique<Widget>(arg1, arg2);

// Array (size known at runtime)
auto arr = std::make_unique<int[]>(100);
arr[0] = 42;
```

`make_unique` forwards its arguments directly to `Widget`'s constructor using perfect forwarding. It never wraps an existing raw pointer — that's the whole point.

## When You Cannot Use make_unique

- **Custom allocators** — `make_unique` always uses global `::operator new`. Use the constructor directly if you need placement new or a pool allocator.
- **Private constructors** — `make_unique` constructs the object internally, so it cannot reach a private constructor even if the caller could. Use a factory pattern instead.
- **Adopting an existing raw pointer** — sometimes a C API returns a heap pointer. You must construct `unique_ptr` from it directly.

## Custom Deleters

By default, `unique_ptr` calls `delete`. For resources that require a different cleanup operation, supply a custom deleter as the second template parameter:

```cpp
// File handle from a C API
FILE* f = fopen("data.bin", "rb");
auto file = std::unique_ptr<FILE, decltype(&fclose)>(f, &fclose);
// fclose(f) is called automatically when file goes out of scope
```

Custom deleters are often function pointers or lambdas:

```cpp
// Lambda deleter
auto buf = std::unique_ptr<uint8_t[], decltype([](uint8_t* p){ free(p); })>(
    static_cast<uint8_t*>(malloc(1024)),
    [](uint8_t* p){ free(p); }
);
```

With C++20 stateless lambdas, the deleter adds no size overhead.

## Deleter as a Struct (Preferred for Reuse)

```cpp
struct FCloseDeleter {
    void operator()(FILE* f) const {
        if (f) fclose(f);
    }
};

using FilePtr = std::unique_ptr<FILE, FCloseDeleter>;

FilePtr openFile(const char* path) {
    return FilePtr(fopen(path, "r"));
}
```

This approach is cleaner, reusable, and the deleter type is part of `FilePtr`'s type, not a hidden implementation detail.

## Size Impact of Stateful Deleters

`unique_ptr` uses the **Empty Base Optimization (EBO)**. A stateless deleter (a function pointer type, a stateless lambda, or an empty struct) adds zero bytes. A stateful deleter (one that captures variables in a lambda, or a struct with data members) increases the size of the `unique_ptr` by the size of the deleter.

| Deleter type | sizeof(unique_ptr<T, D>) |
|---|---|
| Default (`delete`) | `sizeof(T*)` |
| Stateless functor | `sizeof(T*)` (EBO) |
| Function pointer | `sizeof(T*) + sizeof(void(*)())` |
| Stateful lambda | `sizeof(T*) + sizeof(captured state)` |

## Common Pitfalls

- Forgetting the null check inside the deleter for pointer types — `fclose(nullptr)` is undefined behavior on some platforms.
- Using a function pointer deleter when a stateless functor would work — the function pointer doubles the size of the `unique_ptr`.
- Using `make_unique` for an array of known compile-time size — prefer `std::array` instead.

## Interview Answer

**"Why use make_unique instead of new?"**

> `make_unique` eliminates a subtle exception-safety hole in multi-argument function calls and enforces the convention that `unique_ptr` always acquires ownership at construction, making the code easier to audit.
