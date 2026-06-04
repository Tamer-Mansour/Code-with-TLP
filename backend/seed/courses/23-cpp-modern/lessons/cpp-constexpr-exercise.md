# Exercise: constexpr Fibonacci Evaluator

This exercise models C++ `constexpr` evaluation rules — a subtlety that trips up many C++ developers.

A `constexpr` function computes the same mathematical result regardless of context, but the *when* of evaluation differs:

- In a **constexpr context** (array size, template argument, `constexpr` variable): the compiler is **required** to evaluate at compile time
- In a **runtime context** (regular variable, function argument that is not a constant): evaluation happens at runtime
- `IS_CONSTEXPR` with a literal argument is always `YES` — any non-negative integer literal is a compile-time constant in C++

The Fibonacci function (`fib(0)=0, fib(1)=1, fib(n)=fib(n-1)+fib(n-2)`) will be used as the computation. Both contexts produce the same numeric result — only the label differs.

This exercise teaches the important distinction between `constexpr` (can be compile-time) and `consteval` (C++20, must be compile-time).
