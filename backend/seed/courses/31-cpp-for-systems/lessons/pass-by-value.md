# Pass by Value: Copies and Costs

When you pass an argument by value, the function receives its own independent copy of the data. Any modification inside the function leaves the caller's original object untouched. This is the simplest, safest parameter-passing style — but it has a cost that grows with object size.

## How It Works

```cpp
void doubleIt(int n) {   // n is a copy
    n *= 2;
}

int main() {
    int x = 5;
    doubleIt(x);
    std::cout << x;   // still 5 — caller is unaffected
}
```

The moment `doubleIt` is called, the CPU copies the value of `x` into the stack slot for `n`. The two integers are completely independent from that point on.

## The Cost of Copying

For cheap types — `int`, `char`, `double`, pointers — a copy is a single word-sized move and is effectively free. For larger objects the cost scales with the object's size and the complexity of its copy constructor:

```cpp
struct Matrix { double data[1000]; };  // ~8 KB

void processMatrix(Matrix m) { /* ... */ }  // copies 8 KB on every call
```

Profiling regularly reveals unnecessary copies as a bottleneck in data-intensive code. Modern compilers apply **copy elision** (RVO/NRVO) to eliminate some copies, but they cannot eliminate a by-value parameter copy when the caller's object must remain intact.

## When Pass by Value Is Correct

| Scenario | Reason |
|---|---|
| Built-in scalars (`int`, `double`, pointers) | Copy is one instruction; overhead is zero |
| Small POD structs (≤ 2 words) | Fits in registers; no heap involvement |
| The function needs its own mutable working copy | Avoids needing an explicit local copy inside |
| Sink parameters (function will move or consume the value) | Pass by value, then `std::move` — the idiom for constructors |

## Sink Parameter Idiom

When a function is going to store or consume the argument anyway, taking it by value and moving it in is idiomatic modern C++:

```cpp
class Widget {
    std::string name_;
public:
    // Value + move: one copy if lvalue, zero copies if rvalue
    explicit Widget(std::string name) : name_(std::move(name)) {}
};
```

Compare to taking by const reference: that always copies into `name_`. Taking by value lets the compiler eliminate the copy when the caller passes a temporary.

## Worked Example: Stack Simulation

```cpp
#include <iostream>

int pop(int stack[], int& top) {
    return stack[top--];       // no copy of the array (pointer passed)
}

void printSquare(int n) {      // n is a cheap copy — fine
    std::cout << n * n << "\n";
}

int main() {
    printSquare(7);   // 49
    printSquare(12);  // 144
}
```

## Common Pitfalls

- **Copying large objects inadvertently.** A function signature `void process(std::vector<int> v)` copies the entire vector. If you do not need a mutable local copy, use `const std::vector<int>&` instead.
- **Forgetting that copy constructors run.** For types with non-trivial copy constructors (smart pointers, strings, containers), pass-by-value triggers heap allocation or reference counting.
- **Over-optimizing scalars.** Passing `int` by const reference is sometimes seen in legacy code. Modern compilers handle scalars better by value; passing by const ref for `int` adds indirection for no benefit.

## Quick Decision Rule

> Pass by value when the type is cheap to copy (built-in, small POD) **or** when the function is a sink that will own or move the argument.

> **Interview answer:** Pass by value creates an independent copy of the argument. It is safe and simple, but costly for large objects. Use it for cheap types (scalars, small structs) or when the function is a sink that will consume or move the value.
