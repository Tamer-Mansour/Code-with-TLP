# shared_ptr and Reference Counting

When multiple parts of a program need to share ownership of a heap object — and none of them can be designated the single owner — `std::shared_ptr<T>` is the right tool. It tracks how many owners exist using a **reference count** and destroys the managed object only when the last owner releases its share.

## Basic Usage

```cpp
#include <memory>

auto a = std::make_shared<Widget>(42);
auto b = a;                          // b shares ownership
std::cout << a.use_count() << "\n";  // 2

{
    auto c = a;
    // use_count == 3 inside this scope
}   // c destroyed, use_count drops to 2

// a and b still alive
b.reset();                           // use_count == 1
// a goes out of scope -> use_count 0 -> Widget destroyed
```

`use_count()` returns the current reference count. It is provided mainly for debugging; avoid making logic decisions based on it in production code.

## make_shared: The Preferred Constructor

Always prefer `std::make_shared` over constructing with `new`:

```cpp
// Preferred: one heap allocation
auto p = std::make_shared<Widget>(args...);

// Avoid: two heap allocations
std::shared_ptr<Widget> p(new Widget(args...));
```

`make_shared` performs a **single allocation** that holds both the `Widget` and the control block (reference counts). The two-argument form performs two separate allocations. The single-allocation form is faster and produces better cache locality.

## Copying and Moving

```cpp
auto owner1 = std::make_shared<Widget>();
auto owner2 = owner1;           // copy — increments ref count
auto owner3 = std::move(owner1); // move — ref count unchanged, owner1 becomes null
```

Moving is cheaper than copying because it skips the atomic increment of the reference count.

## Passing to Functions

```cpp
// Borrow — does NOT affect reference count
void use(Widget* w);
use(p.get());

// Borrow via shared ownership — increments ref count
void cache(std::shared_ptr<Widget> w);   // pass by value
cache(p);

// Read-only borrow
void inspect(const std::shared_ptr<Widget>& w);  // by const-ref, no copy
```

Passing by value increments the ref count (copy). Passing by `const&` does not. Choose based on whether the callee needs to keep a copy.

## Thread Safety Guarantees

`shared_ptr` reference count operations are **atomic**. Multiple threads can safely copy and destroy `shared_ptr` instances that refer to the same object. However:

- The reference count itself is thread-safe.
- The **managed object** is not automatically thread-safe. If two threads write to `Widget` through their respective `shared_ptr` copies, you still need synchronization.

```
Thread 1: auto copy = sharedPtr;    // safe — atomic ref-count increment
Thread 2: sharedPtr.reset();        // safe — atomic decrement
// But:
Thread 1: p->value = 1;             // NOT safe without mutex if Thread 2 also writes
```

## Aliasing Constructor

`shared_ptr` has a little-known aliasing constructor that lets the pointer address differ from the managed object:

```cpp
auto node = std::make_shared<Node>();
std::shared_ptr<int> field(node, &node->value);
// field.get() == &node->value
// but the ref count belongs to 'node'
```

Useful when exposing a member of a managed object without copying the whole object.

## Common Pitfalls

- **Constructing two `shared_ptr`s from the same raw pointer** — each creates an independent control block with ref count 1. The object is deleted twice.
  ```cpp
  Widget* raw = new Widget();
  std::shared_ptr<Widget> p1(raw);
  std::shared_ptr<Widget> p2(raw);  // UNDEFINED BEHAVIOR: double delete
  ```
- **`enable_shared_from_this` abuse** — calling `shared_from_this()` before a `shared_ptr` to the object exists causes undefined behavior (throws `std::bad_weak_ptr`).
- **Cyclic references** — two objects holding `shared_ptr` to each other leak forever. Use `weak_ptr` to break cycles.

## Interview Answer

**"What is shared_ptr and what is its cost?"**

> `shared_ptr` implements shared ownership through atomic reference counting. Its cost over `unique_ptr` is a heap-allocated control block (avoided if `make_shared` is used), an extra pointer per `shared_ptr` instance, and atomic increment/decrement on copy and destruction — noticeable in hot loops but negligible otherwise.
