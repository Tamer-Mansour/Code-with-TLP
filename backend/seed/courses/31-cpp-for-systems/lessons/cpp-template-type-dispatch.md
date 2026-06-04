# Template Type Dispatcher

This exercise models the behavior of C++ template specialization and `if constexpr` — the compile-time branch elimination that makes zero-cost generic code possible.

## What You Are Building

Read typed values from stdin and apply the correct operation for each type tag. The dispatch logic mirrors what the C++ compiler does when it instantiates a function template for different types.

See the prompt for the full input/output specification.

## The C++ Template Analogy

In real C++, you would write:

```cpp
template<typename T>
void process(T val);

template<>
void process<int>(int val) {
    std::cout << "INT: " << val * 2 << '\n';
}

template<>
void process<float>(float val) {
    std::cout << std::fixed << std::setprecision(2)
              << "FLOAT: " << val << '\n';
}
```

Or with `if constexpr` (preferred in C++17+):

```cpp
template<typename T>
void process(T val) {
    if constexpr (std::is_same_v<T, int>) {
        std::cout << "INT: " << val * 2 << '\n';
    } else if constexpr (std::is_same_v<T, float>) {
        std::cout << std::fixed << std::setprecision(2)
                  << "FLOAT: " << val << '\n';
    }
    // ...
}
```

The key difference from a runtime `if`: each branch is compiled only for the types where it is reachable. Dead branches are not instantiated, preventing compilation errors for operations that don't exist on all types.

## Python Solution Approach

```python
import sys

for _ in range(int(input())):
    parts = input().split(maxsplit=1)
    tag, value = parts[0], parts[1]
    if tag == 'INT':
        print(f'INT: {int(value) * 2}')
    elif tag == 'FLOAT':
        print(f'FLOAT: {float(value):.2f}')
    elif tag == 'STR':
        print(f'STR: {value[::-1]}')
    elif tag == 'BOOL':
        print(f'BOOL: {"true" if value == "1" else "false"}')
```

## SFINAE and Type Traits

Before `if constexpr`, the only way to select behavior at compile time was **SFINAE** (Substitution Failure Is Not An Error) combined with type traits:

```cpp
template<typename T,
         std::enable_if_t<std::is_integral_v<T>, int> = 0>
void process(T val) {
    std::cout << "INT: " << val * 2 << '\n';
}
```

C++20 **Concepts** replace this with readable constraints:

```cpp
template<std::integral T>
void process(T val) {
    std::cout << "INT: " << val * 2 << '\n';
}
```

## Further Reading

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), section T (Templates and generic programming).
- *MIT 6.S096 Effective Programming in C and C++*: [https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/](https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/)
