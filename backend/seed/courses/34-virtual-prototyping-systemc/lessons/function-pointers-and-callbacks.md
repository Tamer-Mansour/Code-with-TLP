# Function Pointers, Functors, and Callbacks

When you register `SC_METHOD(compute)` you are handing a **pointer to a member function** to the SystemC kernel. The kernel stores it and calls it every time the process is triggered. Callbacks, functors, and `std::function` are all variations on this idea — passing behaviour as a value.

## Function Pointers

A function pointer stores the address of a free (non-member) function.

```cpp
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

// Type of a pointer to a function taking two ints, returning int
int (*op)(int, int);

op = add;
std::cout << op(3, 4);   // 7

op = sub;
std::cout << op(3, 4);   // -1
```

The syntax is admittedly awkward. A `typedef` or `using` alias helps:

```cpp
using BinaryOp = int(*)(int, int);
BinaryOp op = add;
```

## Member Function Pointers

A **member function pointer** carries the class type because calling it requires an object:

```cpp
struct Counter {
    int value = 0;
    void increment() { value++; }
    void reset()     { value = 0; }
};

using Method = void(Counter::*)();   // pointer to Counter member

Method m = &Counter::increment;
Counter c;
(c.*m)();    // calls c.increment()
```

This is exactly the underlying mechanism that `SC_METHOD`, `SC_THREAD`, and `SC_CTHREAD` use. The `sc_process_handle` stores the pointer to the module (as `sc_module*`) and the pointer to the member function.

## Functors (Function Objects)

A **functor** is a class with `operator()` overloaded so that instances behave like callable functions:

```cpp
struct Adder {
    int offset;
    Adder(int off) : offset(off) {}
    int operator()(int x) const { return x + offset; }
};

Adder add5(5);
std::cout << add5(3);   // 8
std::cout << add5(10);  // 15
```

Functors can carry **state** (here, `offset`), unlike plain function pointers.

## Lambdas (C++11)

A lambda is syntactic sugar for an anonymous functor:

```cpp
int offset = 5;
auto add5 = [offset](int x) { return x + offset; };
std::cout << add5(3);   // 8
```

Capture list options:

| Capture | Meaning |
|---------|---------|
| `[=]` | Capture all local variables by value |
| `[&]` | Capture all local variables by reference |
| `[x, &y]` | Capture `x` by value, `y` by reference |
| `[]` | Capture nothing |

Lambdas are widely used in SystemC UVM-style testbenches for inline callbacks.

## `std::function`

`std::function<Signature>` is a type-erased wrapper that can hold any callable — function pointer, functor, lambda, or bound member:

```cpp
#include <functional>

std::function<int(int, int)> op;
op = add;                           // function pointer
op = [](int a, int b){ return a*b; }; // lambda
```

`std::function` has a small runtime cost due to type erasure. For performance-critical inner loops, prefer templates.

## `std::bind` and `std::mem_fn`

`std::bind` pre-fills some arguments of a callable:

```cpp
using namespace std::placeholders;
auto add10 = std::bind(add, 10, _1);   // first arg fixed to 10
std::cout << add10(5);   // 15
```

`std::mem_fn` wraps a member function pointer into a callable that accepts the object as its first argument — used in some SystemC helper utilities:

```cpp
auto inc = std::mem_fn(&Counter::increment);
Counter c;
inc(c);   // calls c.increment()
```

## Callbacks in SystemC Models

A common pattern is a configurable monitor that calls back into the testbench:

```cpp
SC_MODULE(Monitor) {
    sc_in<int> data;
    std::function<void(int)> on_data;   // callback hook

    SC_CTOR(Monitor) {
        SC_METHOD(sample);
        sensitive << data;
    }

    void sample() {
        if (on_data) on_data(data.read());
    }
};

// In testbench:
mon.on_data = [](int v) {
    std::cout << "Monitor saw: " << v << "\n";
};
```

## Common Pitfalls

- **Calling through a null function pointer** — always check `ptr != nullptr` or `if (fn)` before calling.
- **Dangling capture by reference** — a lambda that captures a local by reference and outlives that local is undefined behaviour. Capture by value or ensure the lambda does not outlive the captured variable.
- **`std::function` overhead** — wrapping a simple operation in `std::function` and calling it millions of times per simulation cycle can dominate the runtime profile. Benchmark and prefer direct calls or templates if it matters.

> **Interview answer:** Function pointers, functors, and lambdas are all callable objects that allow behaviour to be passed as data. SystemC uses member function pointers internally to store the process callback registered with `SC_METHOD` so the scheduler can invoke the correct member of the correct module instance at the right simulation time.
