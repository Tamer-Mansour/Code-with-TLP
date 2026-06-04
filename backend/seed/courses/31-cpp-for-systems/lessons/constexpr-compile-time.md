# constexpr and Compile-Time Evaluation

`constexpr` is C++'s mechanism for shifting computation from runtime to compile time. In systems programming, this means zero-cost constants, compile-time-verified lookup tables, and type-safe configuration values embedded directly in the binary's read-only data section.

## `const` vs `constexpr`

| Keyword | Evaluated when | Guarantees |
|---|---|---|
| `const` | At runtime (usually) | Value cannot change after initialization |
| `constexpr` | At compile time (required) | Value is a compile-time constant |

```cpp
const int x = std::rand();       // OK: const, but runtime value
constexpr int y = 42;            // OK: compile-time integer constant
constexpr int z = std::rand();   // ERROR: rand() is not constexpr
```

## `constexpr` Functions

A `constexpr` function can be called at compile time if all arguments are constant expressions:

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

constexpr int f6 = factorial(6);   // computed at compile time: 720
int runtime_n = 7;
int fn = factorial(runtime_n);     // falls back to runtime evaluation
```

Since C++14, `constexpr` functions can contain loops and local variables. Since C++20, they can even allocate and deallocate memory using `new`/`delete` within the constant expression.

## Compile-Time Lookup Tables

One of the most powerful applications in systems code is embedding lookup tables as `constexpr` arrays:

```cpp
constexpr auto make_crc_table() {
    std::array<uint32_t, 256> table{};
    for (int i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int j = 0; j < 8; ++j)
            c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        table[i] = c;
    }
    return table;
}
constexpr auto CRC_TABLE = make_crc_table();
```

The entire CRC table lives in `.rodata` with no runtime cost. The compiler verifies its correctness at build time.

## `if constexpr` for Template Branches

In template code, `if constexpr` prunes dead branches at compile time, avoiding instantiation errors:

```cpp
template<typename T>
void serialize(T val) {
    if constexpr (std::is_integral_v<T>) {
        write_int(val);
    } else if constexpr (std::is_floating_point_v<T>) {
        write_float(val);
    }
}
```

Without `if constexpr`, both branches would need to compile for every `T`, causing errors when the wrong overload doesn't exist.

## The `as-if` Rule and Compiler Optimizations

`constexpr` interacts with the compiler's **as-if rule**: the compiler may transform code in any way that produces the same observable behavior. A `constexpr` value that the compiler can prove constant at compile time will be folded into a literal, eliminating the computation entirely — even without `constexpr` on the variable. The explicit `constexpr` keyword documents the intent and makes the compiler enforce it.

## Key Myth Correction

A common myth: *"C++ templates always cause code bloat and should be minimized."* This is false. `constexpr` and templates together enable **zero-cost abstractions** — the compiler generates exactly the same machine code as hand-written C. For example, `std::array<int, 4>` compiles to the same code as `int[4]`. The linker merges identical instantiations under the ODR.

## Further Reading

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), rule **Con.5**: Use `constexpr` for values that can be computed at compile time.
- *MIT 6.S096 Effective Programming in C and C++*: [https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/](https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/)
