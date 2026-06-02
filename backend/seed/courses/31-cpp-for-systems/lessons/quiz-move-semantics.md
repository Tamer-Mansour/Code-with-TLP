# Quiz: Move Semantics and the Rule of Five/Zero

Test your understanding of move semantics, value categories, and modern C++ ownership design.

---

**Q1. What does `std::move(x)` actually do at runtime?**

- [ ] Copies the bytes of `x` into a new memory location
- [ ] Calls the move constructor of `x`
- [x] Casts `x` to an rvalue reference (xvalue) — no bytes are moved
- [ ] Marks `x` as destroyed and deallocates its memory

The actual resource transfer happens in the move constructor or move assignment operator that is called because of the cast. `std::move` itself is a zero-cost, compile-time operation.

---

**Q2. You have the following class. What happens when elements are added to a `std::vector<Widget>` and a reallocation occurs?**

```cpp
class Widget {
    int* data_;
public:
    Widget() : data_(new int(0)) {}
    ~Widget() { delete data_; }
    Widget(Widget&& o) : data_(o.data_) { o.data_ = nullptr; } // no noexcept
    Widget(const Widget& o) : data_(new int(*o.data_)) {}
};
```

- [ ] Elements are moved using the move constructor
- [x] Elements are copied using the copy constructor, because the move constructor is not `noexcept`
- [ ] The program crashes with a double-free error
- [ ] Compilation fails because both copy and move constructors are defined

`std::vector` checks `std::is_nothrow_move_constructible` before deciding to move or copy during reallocation. Without `noexcept`, it falls back to copying to preserve the strong exception guarantee.

---

**Q3. Which of the following is a forwarding reference (universal reference)?**

```cpp
// A
void f(std::string&& s);

// B
template<typename T>
void g(T&& t);

// C
template<typename T>
void h(std::vector<T>&& v);

// D
void k(auto&& x);
```

- [ ] A only
- [x] B and D
- [ ] A, B, and C
- [ ] All of the above

A is a plain rvalue reference (concrete type). B is a forwarding reference because `T` is directly deduced. C is an rvalue reference because the deduced part (`T`) is inside the template argument, not `T` itself. D uses abbreviated function template syntax — `auto&&` is a forwarding reference.

---

**Q4. A class defines a destructor but no other special member functions. Which statement is TRUE?**

- [ ] The compiler generates copy and move operations as if the destructor were not defined
- [ ] The compiler deletes all five special member functions
- [x] The compiler deletes the implicit move constructor and move assignment; copy operations are generated (deprecated behavior)
- [ ] The compiler generates all five automatically

Defining a destructor suppresses the implicit move constructor and move assignment (they are defined as deleted). Copy operations are still generated but this is considered deprecated behavior in C++11/14. The Rule of Five: define one, define all five.

---

**Q5. What is the output of the following program?**

```cpp
#include <iostream>
#include <string>

void process(std::string&& s) {
    std::string local = s; // note: not std::move(s)
    std::cout << s << "\n";
}

int main() {
    process(std::string{"hello"});
}
```

- [ ] (empty line — s is moved from)
- [x] `hello` — s is copied because named rvalue refs are lvalues
- [ ] Undefined behavior — s is a dangling reference
- [ ] Compilation error — cannot copy from `string&&`

Inside `process`, `s` is a **named** rvalue reference — it is an lvalue. `std::string local = s` calls the copy constructor, leaving `s` intact with the value `"hello"`. To move it, you would write `std::string local = std::move(s)`.

---

**Q6. Which design approach is preferred for a class that holds a `std::vector<int>` and a `std::string`?**

```cpp
// Option A
class DataSet {
    std::vector<int> values_;
    std::string      label_;
public:
    ~DataSet() { /* ... */ }
    DataSet(const DataSet&) { /* copy */ }
    DataSet& operator=(const DataSet&) { /* copy assign */ return *this; }
    DataSet(DataSet&&) noexcept { /* move */ }
    DataSet& operator=(DataSet&&) noexcept { /* move assign */ return *this; }
};

// Option B
class DataSet {
    std::vector<int> values_;
    std::string      label_;
    // No special members defined
};
```

- [ ] Option A — always define all five for safety
- [x] Option B — Rule of Zero; compiler generates correct and efficient special members
- [ ] Option A — you must define the destructor to free `values_` and `label_`
- [ ] Option B only works if `DataSet` is not stored in containers

Option B applies the Rule of Zero. Both `std::vector` and `std::string` are proper RAII types with correct copy and move operations. The compiler-generated special members delegate to each member's operations, giving you correct behavior for free. Option A is error-prone boilerplate that adds no value here.
