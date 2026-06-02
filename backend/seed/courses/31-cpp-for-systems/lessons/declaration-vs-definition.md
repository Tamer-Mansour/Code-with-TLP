# Declaration vs Definition: What Is the Difference?

One of the most common sources of confusion — and compiler/linker errors — in C++ is the distinction between a **declaration** and a **definition**. The rule sounds simple but has many edge cases that trip up experienced developers.

## The Core Distinction

A **declaration** tells the compiler that a name exists and what its type is. No storage is allocated, no code is generated.

A **definition** is a declaration that also provides the full implementation or allocates storage. Every definition is also a declaration, but not every declaration is a definition.

```cpp
// DECLARATION — compiler knows 'add' takes two ints and returns int
int add(int a, int b);

// DEFINITION — compiler generates machine code for 'add'
int add(int a, int b) {
    return a + b;
}
```

## Variables: Declaration vs Definition

```cpp
extern int counter;   // declaration — "counter exists somewhere else"
int counter;          // definition  — allocates 4 bytes in this TU
int counter = 42;     // definition  — allocates and initializes
```

The `extern` keyword says "I am telling you this name exists, but I am not creating it here." If no TU ever provides the definition, the linker will report an undefined reference.

## Classes: Declaration vs Definition

A **class declaration** (forward declaration) gives just enough information to use the type through a pointer or reference:

```cpp
class Widget;              // forward declaration — incomplete type

Widget* ptr;               // OK — pointer to incomplete type
// Widget w;               // ERROR — size unknown, cannot instantiate
// ptr->draw();            // ERROR — members unknown
```

A **class definition** provides the full body:

```cpp
class Widget {             // definition — complete type
public:
    void draw();
    int width;
};
```

Note: the class definition does NOT define the member function `draw()`. That still needs a separate definition:

```cpp
void Widget::draw() {      // definition of the member function
    // ...
}
```

## Inline Functions and Templates

`inline` functions and function templates are special: their **definition must appear in every translation unit that uses them**. This is why they live in headers:

```cpp
// In a header — definition is fine here
inline int square(int x) { return x * x; }

template<typename T>
T clamp(T val, T lo, T hi) {
    return val < lo ? lo : (val > hi ? hi : val);
}
```

Without `inline`, placing a function definition in a header and including it in two `.cpp` files would violate the One Definition Rule.

## Quick Reference Table

| Construct | Is it a declaration? | Is it a definition? |
|---|---|---|
| `int foo(int);` | Yes | No |
| `int foo(int x) { return x; }` | Yes | Yes |
| `extern int g;` | Yes | No |
| `int g;` | Yes | Yes |
| `class Foo;` | Yes | No |
| `class Foo { int x; };` | Yes | Yes |
| `void Foo::bar() { }` | Yes | Yes |
| `typedef int MyInt;` | Yes | No |

## Worked Example — Tracing the Error

```cpp
// widget.h
class Widget {
public:
    void draw();   // declaration of draw
};

// widget.cpp
#include "widget.h"
// Forgot to define draw() here!

// main.cpp
#include "widget.h"

int main() {
    Widget w;
    w.draw();   // compiler: fine, sees declaration
                // linker: ERROR — undefined reference to Widget::draw()
}
```

The compiler accepts `w.draw()` because it has the declaration. The linker fails because no translation unit provided the definition. Adding `void Widget::draw() { }` in `widget.cpp` fixes it.

## Common Pitfalls

- **Declaration without definition** — code compiles but the linker complains.
- **Definition without accessible declaration** — calling a function defined later in the same file without a forward declaration (C-style issue, less common in C++).
- **Confusing class definition with object instantiation** — `class Foo { };` defines the type, not an object. `Foo f;` defines an object.
- **Putting non-inline function definitions in headers** — multiple TUs each get their own copy → multiple-definition linker error.

> **Interview answer:** "A declaration tells the compiler a name exists and its type; a definition provides the full implementation or allocates storage. The linker needs exactly one definition of every used symbol. Compiler errors come from missing declarations; linker errors come from missing definitions."
