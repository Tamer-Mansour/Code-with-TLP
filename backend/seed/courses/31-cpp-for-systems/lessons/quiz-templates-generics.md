# Quiz: Templates and Generic Programming

**Q1. What does SFINAE stand for, and when does it apply?**

- [ ] "Static Function Instantiation And Elimination" — it applies when a function is declared but never called.
- [ ] "Substitution Failure Is Not Allowed" — it causes a hard compilation error when a template argument fails substitution.
- [x] "Substitution Failure Is Not An Error" — when substituting a template argument causes an invalid type expression, that specialization is silently removed from the overload set rather than causing a compile error.
- [ ] "Simple Function Inlining And Expansion" — it controls whether the compiler inlines a template function.

SFINAE is the mechanism that makes overload-set-based template selection possible. The compiler silently discards a template specialization if substituting the deduced types into the function signature produces an invalid expression, allowing a different overload to be selected.

---

**Q2. What is the output of the following code?**

```cpp
template<typename T>
void show(T x) { std::cout << "generic\n"; }

template<>
void show<int>(int x) { std::cout << "int\n"; }

void show(double x) { std::cout << "double\n"; }

show(1.0f);
```

- [ ] `int`
- [ ] `generic`
- [x] `generic`
- [ ] `double`

`1.0f` is a `float`. The non-template overload `show(double)` requires an implicit conversion. The function template `show<float>` is an exact match, so it wins over the non-template overload that requires conversion. Output: `generic`.

---

**Q3. Which C++20 feature replaces verbose `std::enable_if` constraints with readable syntax?**

- [ ] `static_assert`
- [ ] `if constexpr`
- [x] Concepts (`requires` and named concept constraints)
- [ ] `decltype`

C++20 Concepts allow writing `template<std::integral T>` instead of `template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>`. They also produce better compiler error messages when constraints are violated.

---

**Q4. Why should the implementation of a function template typically live in the header file, not a .cpp file?**

- [ ] The linker cannot find template instantiations in .cpp files.
- [x] The compiler needs to see the full template definition at every point of instantiation; instantiating in one .cpp file does not generate code for types used in other .cpp files.
- [ ] Function templates must be inline, which requires header placement.
- [ ] Header files are compiled with higher optimization levels than .cpp files.

Template instantiation happens at the point of use. If the template body is in a separate .cpp file, the compiler cannot instantiate it for types used in other translation units. The solution is to define the template in the header or use explicit instantiation declarations.

---

**Q5. What does `std::forward<T>(x)` do differently from `std::move(x)`?**

- [ ] `std::forward` moves unconditionally; `std::move` moves only if the object is an rvalue.
- [ ] They are identical; `std::forward` is just an alias for `std::move`.
- [x] `std::forward<T>(x)` preserves the value category of `x` — it casts to rvalue only if `T` was deduced as an rvalue reference type. `std::move(x)` always casts to rvalue regardless of the original category.
- [ ] `std::forward` is safe for non-movable types; `std::move` throws for non-movable types.

`std::forward` is used in forwarding (universal) reference contexts to preserve whether an argument was passed as an lvalue or rvalue. `std::move` unconditionally casts to rvalue, which would incorrectly move from lvalue arguments if used in a generic wrapper.

---

**Q6. A variadic template function template is defined as `template<typename... Args> void log(Args&&... args)`. What does the `...` after `Args&&` mean in the call `log(std::forward<Args>(args)...)`?**

- [ ] It repeats `std::forward<Args>(args)` exactly three times.
- [ ] It creates a tuple from all arguments.
- [x] It expands the parameter pack, applying `std::forward<Arg_i>(arg_i)` for each argument independently.
- [ ] It enables variadic printf-style formatting.

Pack expansion (`...`) applies the pattern to each element of the parameter pack simultaneously. `std::forward<Args>(args)...` expands to `std::forward<A0>(a0), std::forward<A1>(a1), ...` — perfect forwarding each argument to the wrapped call.
