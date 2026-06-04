# Exercise: Move Semantics Value Category Classifier

Practice your understanding of C++ value categories by classifying expressions as **LVALUE**, **RVALUE**, or **XVALUE** based on the Modern C++ rules you have learned.

Key rules to remember:

- A named variable of any type → **LVALUE** (even if declared as `T&&`)
- A literal (integer, string, float) → **RVALUE** (prvalue)
- A function call returning `T` (non-reference) → **RVALUE**
- A function call returning `T&` → **LVALUE**
- `std::move(x)` result → **XVALUE**
- A named rvalue reference variable used by name → **LVALUE**
- A temporary object created inline (e.g., `MyClass()`) → **RVALUE**

This exercise will test whether you truly grasp why `std::move` must be called again on named rvalue reference variables, and why forwarding references behave differently from rvalue references.
