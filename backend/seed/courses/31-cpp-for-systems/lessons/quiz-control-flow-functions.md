# Quiz: Control Flow and Functions

Test your understanding of branching, loops, and function mechanics from this module.

---

**Q1. Which of the following loop forms is guaranteed to execute its body at least once?**

- [ ] `for (int i = 0; i < 0; ++i)`
- [ ] `while (false)`
- [x] `do { ... } while (false);`
- [ ] `for (;;)` with an immediate `break`

_A `do-while` loop tests the condition **after** the body, so the body always runs at least once regardless of the condition._

---

**Q2. What is the output of the following code?**

```cpp
void f(int);
void f(double);

int main() { f('A'); }
```

- [ ] Calls `f(double)` because `char` promotes to `double`
- [x] Calls `f(int)` because `char` undergoes integral promotion to `int`
- [ ] Ambiguous — compile error
- [ ] Calls neither — `char` has no matching overload

_Integral promotion rules: `char`, `short`, and `bool` promote to `int` before any other conversion is considered. `double` would require a further standard conversion, so `f(int)` wins._

---

**Q3. Where should default argument values be placed when a function has a separate declaration and definition?**

- [x] In the declaration (e.g., in the header file)
- [ ] In the definition (e.g., in the .cpp file)
- [ ] In both the declaration and the definition — they must match
- [ ] Either location is fine; the compiler merges them

_Default arguments must appear in the declaration. Re-specifying them in the definition is a compile error. Placing them in the header makes the defaults visible to all callers._

---

**Q4. What is the PRIMARY purpose of the `inline` keyword in modern C++?**

- [ ] Force the compiler to eliminate the function call overhead
- [ ] Prevent the function from being visible outside the translation unit
- [x] Allow a function definition to appear in multiple translation units without violating the One Definition Rule
- [ ] Enable recursive functions to be optimized by the compiler

_While `inline` historically hinted at call-site substitution, compilers ignore that hint and inline based on their own heuristics. The real, guaranteed effect is ODR relaxation: the linker merges duplicate definitions of the same `inline` function._

---

**Q5. What happens when a `switch` statement falls through from one `case` to the next without a `break`?**

- [ ] A compile error is issued
- [ ] The program terminates with undefined behavior
- [x] Execution continues into the next `case` block
- [ ] The `default` case is executed instead

_Fall-through is legal and intentional in C++. The `[[fallthrough]]` attribute (C++17) documents intentional fall-through and silences compiler warnings. Unintentional fall-through is a common source of bugs._

---

**Q6. Which statement about recursion and the call stack is TRUE?**

- [ ] Each recursive call reuses the same stack frame, so stack depth is always O(1)
- [ ] The C++ standard guarantees tail-call optimization for tail-recursive functions
- [x] Each recursive call pushes a new stack frame; excessive depth causes a stack overflow
- [ ] Recursive functions are always slower than iterative equivalents due to function-call overhead

_Every call — recursive or not — pushes a new frame. C++ does not standardize tail-call optimization (unlike some functional languages). TCO may or may not be applied by a specific compiler at a specific optimization level._

---
