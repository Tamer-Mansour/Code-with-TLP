# Move Semantics and Rvalue References

Move semantics — introduced in C++11 — let you **transfer** ownership of resources from one object to another without copying them. This is the mechanism that makes returning large objects from functions cheap and makes `std::unique_ptr` non-copyable but movable.

## Value Categories

Every C++ expression has a type and a **value category**:

| Category | Meaning | Example |
|----------|---------|---------|
| **lvalue** | Has a name / address | `x`, `obj.field` |
| **rvalue** | Temporary, no address | `42`, `x + y`, `f()` |
| **xvalue** | "expiring" lvalue after `std::move` | `std::move(x)` |

Rvalues and xvalues are collectively called **rvalues**. They can bind to rvalue references (`T&&`).

## Rvalue References (`T&&`)

```cpp
int x = 5;
int&  lref  = x;     // lvalue reference — OK
int&& rref  = 5;     // rvalue reference — binds to temporary
int&& rref2 = std::move(x);  // xvalue — x is "about to die"
```

An rvalue reference tells the compiler: "I'm allowed to steal this object's guts."

## The Move Constructor

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    // Copy constructor — expensive O(n) allocation
    Buffer(const Buffer& other)
        : size_(other.size_), data_(new char[other.size_])
    {
        std::memcpy(data_, other.data_, size_);
    }

    // Move constructor — O(1) pointer theft
    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_)
    {
        other.data_ = nullptr;   // leave source in valid, empty state
        other.size_ = 0;
    }

    ~Buffer() { delete[] data_; }
};
```

After the move, `other` is in a valid-but-unspecified state — you can destroy it or reassign it, but you should not read its contents.

## std::move

`std::move` is just a cast to an rvalue reference — it does not move anything by itself. It signals *intent*:

```cpp
std::vector<std::string> words;
std::string s = "hello";
words.push_back(std::move(s));   // s's buffer is stolen; s is now empty
```

Without `std::move`, `push_back` would copy `s`. With it, the internal buffer is transferred in O(1).

## The Rule of Five

If you define any one of the five special member functions, define all five:

1. Destructor
2. Copy constructor
3. Copy assignment operator
4. Move constructor
5. Move assignment operator

```cpp
class Foo {
public:
    Foo();
    ~Foo();
    Foo(const Foo&);             // copy ctor
    Foo& operator=(const Foo&);  // copy assign
    Foo(Foo&&) noexcept;         // move ctor
    Foo& operator=(Foo&&) noexcept; // move assign
};
```

In practice, the **Rule of Zero** is preferred: design your class so the compiler-generated defaults work correctly (use smart pointers and RAII members instead of raw resources).

## Perfect Forwarding

Function templates sometimes need to forward arguments to another function preserving value category. Use `std::forward`:

```cpp
template<typename T>
void wrapper(T&& arg) {
    target(std::forward<T>(arg));   // forwards lvalue as lvalue, rvalue as rvalue
}
```

`T&&` in a template context is a **forwarding reference** (also called universal reference), not a plain rvalue reference.

## Performance Impact

Move semantics make returning large objects from functions practically free via **Named Return Value Optimization (NRVO)** and move construction:

```cpp
std::vector<int> buildLargeVector() {
    std::vector<int> v(1'000'000);
    // ... fill v ...
    return v;   // NRVO or move — no copy
}
```

With C++11 or later, this pattern is idiomatic and efficient.
