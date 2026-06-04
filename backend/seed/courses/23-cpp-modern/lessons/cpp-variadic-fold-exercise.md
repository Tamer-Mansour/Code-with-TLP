# Exercise: Variadic Template Argument Pack Expander

C++17 introduced **fold expressions** that reduce a parameter pack with a binary operator in a single expression:

```cpp
// Left fold: ((v1 + v2) + v3) + v4
template <typename... Args>
auto sum(Args... args) {
    return (... + args);
}

// Right fold: v1 + (v2 + (v3 + v4))
template <typename... Args>
auto sum_right(Args... args) {
    return (args + ...);
}
```

This exercise simulates the evaluation of fold expressions and pack introspection operations. You will compute:

- `LEFT_FOLD op values`: left-associative reduction `(((v1 op v2) op v3) ...)`
- `RIGHT_FOLD op values`: right-associative reduction `(v1 op (v2 op (...vN)))`
- `SIZEOF_PACK values`: count of elements (mirrors `sizeof...(pack)` in C++)

Supported operators: `+`, `-`, `*`, `MAX` (takes the maximum of two values).

This directly models compile-time computations that C++ programmers write using variadic templates, making it concrete and testable.
