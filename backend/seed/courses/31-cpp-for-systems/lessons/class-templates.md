# Class Templates and Instantiation

A **class template** defines a family of classes parameterized by types (or values). Every container in the standard library — `vector<T>`, `map<K,V>`, `optional<T>` — is a class template. Writing your own lets you build reusable, type-safe data structures without code duplication.

## Defining a Class Template

```cpp
template <typename T>
class Stack {
public:
    void push(const T& val) { data_.push_back(val); }
    void pop()              { data_.pop_back(); }
    const T& top() const    { return data_.back(); }
    bool empty() const      { return data_.empty(); }
    std::size_t size() const { return data_.size(); }

private:
    std::vector<T> data_;
};
```

Usage:

```cpp
Stack<int>         ints;
Stack<std::string> words;

ints.push(42);
words.push("hello");
```

`Stack<int>` and `Stack<std::string>` are entirely separate types — the compiler generates distinct code for each.

## Member Functions Outside the Class Definition

When you define a member function outside the class body you must repeat the template header:

```cpp
template <typename T>
class Box {
public:
    explicit Box(T v);
    T value() const;
private:
    T v_;
};

template <typename T>
Box<T>::Box(T v) : v_(v) {}

template <typename T>
T Box<T>::value() const { return v_; }
```

This is verbose but necessary. The definition must still live in the header (or a `.tpp` file that the header `#include`s) so every translation unit can see it.

## Multiple Template Parameters

```cpp
template <typename K, typename V>
class Pair {
public:
    Pair(K k, V v) : key_(k), val_(v) {}
    K key()   const { return key_; }
    V value() const { return val_; }
private:
    K key_;
    V val_;
};

Pair<std::string, int> score{"Alice", 95};
```

## Non-Type Template Parameters in Classes

```cpp
template <typename T, std::size_t N>
class FixedArray {
public:
    T& operator[](std::size_t i)       { return data_[i]; }
    const T& operator[](std::size_t i) const { return data_[i]; }
    constexpr std::size_t size() const { return N; }
private:
    T data_[N];
};

FixedArray<int, 4> arr;
arr[0] = 10;
```

`FixedArray<int, 4>` and `FixedArray<int, 8>` are **distinct types**. This is how `std::array<T, N>` works under the hood — zero-overhead fixed-size array on the stack.

## Default Template Arguments

```cpp
template <typename T, typename Allocator = std::allocator<T>>
class MyVector { /* ... */ };

MyVector<int>              v1;   // uses default allocator
MyVector<int, PoolAlloc>   v2;   // uses custom allocator
```

Default arguments make templates ergonomic while remaining flexible for advanced users.

## Instantiation: Implicit vs Explicit

**Implicit instantiation** — the compiler generates code when you first use a template with a given set of arguments. Only member functions that are actually called are instantiated (lazy instantiation).

**Explicit instantiation** — forces the compiler to generate all member functions for a specific set of arguments:

```cpp
// In one .cpp file:
template class Stack<int>;   // generates all Stack<int> members

// In all other .cpp files (after seeing the class definition):
extern template class Stack<int>;  // tells the linker: defined elsewhere
```

Explicit instantiation reduces compile times in large projects by avoiding repeated generation in every translation unit.

## Worked Example: A Generic Ring Buffer

```cpp
template <typename T, std::size_t Cap>
class RingBuffer {
public:
    bool push(const T& v) {
        if (full()) return false;
        buf_[head_] = v;
        head_ = (head_ + 1) % Cap;
        ++count_;
        return true;
    }
    T pop() {
        T v = buf_[tail_];
        tail_ = (tail_ + 1) % Cap;
        --count_;
        return v;
    }
    bool empty() const { return count_ == 0; }
    bool full()  const { return count_ == Cap; }
private:
    T buf_[Cap]{};
    std::size_t head_{0}, tail_{0}, count_{0};
};

RingBuffer<int, 8> rb;
rb.push(1); rb.push(2);
int x = rb.pop();  // x == 1
```

## Common Pitfalls

- **Template definitions in `.cpp` files**: causes linker errors in other translation units. Always put definitions in headers unless using explicit instantiation.
- **Dependent name lookup**: inside a template, `this->member` or `Base<T>::member` must be used to access names from a dependent base class; otherwise the compiler ignores them.
- **Bloat**: each unique instantiation generates its own machine code. Factor out non-type-dependent logic into a non-template base class to reduce binary size.

> **Interview answer:** "A class template is a compile-time blueprint that generates a distinct class for each unique set of template arguments. Member functions are instantiated lazily — only when called. Definitions must be in headers (or use explicit instantiation) because the compiler needs them at the point of use."
