# Exercise: Smart Pointer Reference Count Simulator

`std::shared_ptr` uses **reference counting** to manage object lifetimes. Every copy of a `shared_ptr` to the same object increments a counter; every reset or destruction decrements it. When the count reaches zero, the object is destroyed.

In this exercise you simulate the exact lifecycle of shared pointers: creation, copying, resetting, and moving. You will track which object each pointer owns and print the reference count changes as they happen.

Key behaviors to internalize:

- `MAKE` — new object, count starts at 1
- `COPY` — new shared owner, count increments
- `RESET` — one owner gone; if count hits 0, object is destroyed
- `MOVE` — ownership transfers; source pointer becomes empty, count is unchanged

This mirrors real `std::shared_ptr` semantics from `<memory>`. Understanding these rules prevents use-after-free bugs and reference cycle leaks in production C++ code.
