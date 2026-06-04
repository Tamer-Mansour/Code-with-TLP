# Exercise: Template Instantiation Depth Checker

C++ compilers impose a limit on recursive template instantiation depth (typically 900 levels in GCC/Clang). Exceeding this limit causes a hard compile error. This exercise simulates that compiler behavior.

You are given a set of template definitions where each template can trigger instantiation of other templates. Starting from a root template, compute:

1. The total number of **unique** templates instantiated (no double-counting)
2. Whether the recursion depth exceeds the given limit
3. The path at which the limit was first hit (if any)

This models real-world scenarios: deeply recursive type lists (`TypeList<A, TypeList<B, ...>>`), factorial template metaprogramming (`Factorial<N>` instantiates `Factorial<N-1>`), and complex trait chains. Understanding instantiation depth helps you write compile-time code that stays within compiler limits.

**Hint:** Use depth-first search and track the maximum depth reached from the starting node.
