# Exercise: RAII Resource Tracker Simulation

RAII means resources tied to object lifetimes are automatically released when those objects go out of scope. This exercise simulates that behavior without writing a single line of C++.

You will process a sequence of resource operations and produce output that matches exactly what a correct RAII implementation would produce:

- Resources acquired in a scope are released in **reverse acquisition order** when `SCOPE_END` is reached
- Explicit `RELEASE` operations happen immediately
- Double-releasing a resource is an error

This mirrors what `std::unique_ptr`, `std::lock_guard`, and `std::fstream` do automatically at the end of each C++ scope. Understanding the ordering (LIFO — last in, first out) is key: destructors run in the reverse order of construction, just like stack unwinding.
