# unique_ptr: Exclusive Ownership

`std::unique_ptr<T>` is the workhorse of modern C++ memory management. It expresses the simplest and most common ownership pattern: exactly one piece of code owns the heap object, and when that owner is done, the object is destroyed.

## Declaring and Using unique_ptr

```cpp
#include <memory>

std::unique_ptr<int> p = std::make_unique<int>(42);
std::cout << *p << "\n";   // 42 — dereference like a raw pointer
p->doWork();               // -> works too
```

When `p` goes out of scope, the managed `int` is automatically deleted. No `delete` call required.

## Move-Only Semantics

`unique_ptr` cannot be copied — copying would create two owners, which violates exclusive ownership. It can only be **moved**:

```cpp
auto a = std::make_unique<Widget>();
auto b = std::move(a);   // ownership transfers to b
// a is now null; b owns the Widget
```

Attempting to copy produces a compile error:

```cpp
auto c = a;  // ERROR: use of deleted function
```

This is a feature, not a limitation. The compiler enforces ownership discipline at compile time.

## Passing unique_ptr to Functions

There are three idiomatic patterns:

```cpp
// 1. Transfer ownership into the function
void sink(std::unique_ptr<Widget> w);
sink(std::move(myWidget));    // caller loses ownership

// 2. Borrow without transfer — caller keeps ownership
void use(Widget* w);          // or const Widget&
use(myWidget.get());          // .get() returns the raw pointer

// 3. Borrow via reference to unique_ptr (rare, usually a smell)
void inspect(const std::unique_ptr<Widget>& w);
```

The most important rule: pass `unique_ptr` by value only when you mean to transfer ownership. Otherwise pass a raw pointer or reference to the underlying object.

## Returning unique_ptr from Functions

Returning a `unique_ptr` is the standard way to express "this function creates an object and gives you ownership":

```cpp
std::unique_ptr<Widget> createWidget(int id) {
    return std::make_unique<Widget>(id);  // NRVO or implicit move
}

auto w = createWidget(7);  // w owns the Widget
```

This is exception-safe — if the caller's stack unwinds, `w`'s destructor cleans up.

## Checking for Null

`unique_ptr` converts to `bool`:

```cpp
if (p) {
    p->run();
}
// equivalent to: if (p.get() != nullptr)
```

## Releasing and Resetting

```cpp
Widget* raw = p.release();  // p gives up ownership; raw is now YOUR problem
p.reset();                  // deletes current object, p becomes null
p.reset(new Widget());      // deletes old object, takes ownership of new one
```

Prefer `reset()` over `release()`. Calling `release()` puts you back in manual memory management territory.

## unique_ptr with Polymorphism

`unique_ptr` works naturally with inheritance:

```cpp
std::unique_ptr<Base> b = std::make_unique<Derived>();
b->virtualMethod();  // dispatches correctly
// ~Derived() called when b goes out of scope (requires virtual destructor in Base)
```

Always declare a virtual destructor in a polymorphic base class.

## Zero Overhead

`unique_ptr` has **no runtime overhead** compared to a raw owning pointer. The size is exactly one pointer (unless a custom deleter with state is used). The destructor call is inlined and optimized away. There is no reference counting, no heap allocation for the control block — nothing extra.

## Common Pitfalls

- Constructing from a raw pointer obtained via `.get()` of another `unique_ptr` — creates two owners.
- Storing `.get()` and using it after the `unique_ptr` is destroyed — dangling pointer.
- Forgetting `std::move()` when passing to a sink function — causes a compile error that is easy to misread.

## Interview Answer

**"What is unique_ptr and when do you use it?"**

> `unique_ptr` is a move-only RAII wrapper that gives a single owner exclusive control over a heap object. It has zero overhead versus a raw pointer and should be the default choice whenever heap allocation is needed and ownership is clear.
