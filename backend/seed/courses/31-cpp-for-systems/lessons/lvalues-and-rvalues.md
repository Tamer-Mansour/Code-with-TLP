# lvalues, rvalues, and Value Categories

Understanding value categories is the foundation for move semantics. Before C++11, most developers thought of expressions as simply "things with addresses" or "temporary results." The modern standard gives us a precise taxonomy that drives how the compiler decides when to copy and when to steal.

## The Core Distinction

Every expression in C++ has a type and a **value category**. The primary categories are:

| Category | Has identity? | Movable? | Common example |
|----------|--------------|----------|----------------|
| lvalue   | Yes          | No*      | Named variable, `*ptr`, `arr[0]` |
| xvalue   | Yes          | Yes      | Result of `std::move(x)`, `T&&` cast |
| prvalue  | No           | Yes      | Literal `42`, temporary `T{}`, returned-by-value |

- **lvalue** — "left-hand-side value." Has a persistent identity (an address you can take with `&`). Lives beyond the current expression.
- **prvalue** — "pure right-hand value." A temporary with no named location; gone after the statement.
- **xvalue** — "expiring value." Has identity but you have explicitly signaled it is safe to move from.

Collectively, lvalue + xvalue = **glvalue** (generalized lvalue). xvalue + prvalue = **rvalue**.

## Practical Examples

```cpp
int a = 10;        // 'a' is an lvalue — has address, can appear on left
int b = a + 3;     // 'a+3' is a prvalue — temporary int, no address
int&& r = a + 3;   // binds rvalue reference to prvalue — extends lifetime

std::string s1 = "hello";
std::string s2 = std::move(s1); // std::move casts s1 to xvalue
                                 // s1 is now in valid-but-unspecified state
```

The rule of thumb: **if you can put `&` in front of an expression and get its address, it is an lvalue (or xvalue). If it would be a compile error, it is a prvalue.**

```cpp
int* p = &42;        // ERROR: cannot take address of prvalue
int x = 5;
int* q = &x;         // OK: x is lvalue
int* r = &std::move(x); // OK: xvalue still has identity
```

## Why Does This Matter?

The compiler uses value categories to choose between overloads:

```cpp
void process(const std::string& s) { /* copy path */ }
void process(std::string&& s)      { /* move path */ }

std::string name = "Alice";
process(name);              // calls lvalue overload — copy
process(std::string{"Bob"}); // calls rvalue overload — move (no copy)
process(std::move(name));   // explicitly request move overload
```

This is the engine behind move semantics: prvalues and xvalues bind to `T&&`, while lvalues bind to `T&` or `const T&`.

## Common Pitfall: Named rvalue References Are lvalues

This trips up most developers the first time:

```cpp
void foo(std::string&& s) {
    // Inside the body, 's' is an lvalue!
    // It has a name, so it has identity.
    std::string copy = s;          // copies, does NOT move
    std::string moved = std::move(s); // explicit cast to xvalue — moves
}
```

A parameter of type `T&&` is an rvalue reference, but the **named variable itself** is an lvalue inside the function body.

## Lifetime Extension

A const lvalue reference or rvalue reference bound to a prvalue extends that temporary's lifetime to match the reference:

```cpp
const std::string& ref = std::string{"temp"}; // lifetime extended
std::string&& rref = std::string{"temp"};      // also extended
// Both are valid to use here
```

> **Interview answer:** An lvalue has a persistent identity and addressable location; an rvalue (prvalue or xvalue) is a temporary or explicitly expiring value. The distinction tells the compiler when it is safe to move-from instead of copy.
