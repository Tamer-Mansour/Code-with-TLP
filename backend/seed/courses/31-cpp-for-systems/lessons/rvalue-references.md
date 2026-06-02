# Rvalue References and &&

C++11 introduced the **rvalue reference** (`T&&`) as a new kind of reference that binds exclusively to rvalues. It is the syntactic foundation that makes move semantics and perfect forwarding possible.

## Syntax and Binding Rules

```cpp
int   x  = 5;
int&  lref = x;       // lvalue reference — binds to lvalue
int&& rref = 5;       // rvalue reference — binds to prvalue
int&& rref2 = x + 1;  // binds to prvalue (result of expression)

// int&& bad = x;     // ERROR: cannot bind rvalue ref to lvalue
```

The double ampersand `&&` signals "I accept a temporary (or explicitly moved-from) object, and I promise to handle it as such."

## Why Not Just Use const T&?

Before C++11, `const T&` was the canonical way to accept temporaries without copying. But it has a critical limitation: `const` means you cannot modify the object, so you cannot *steal* its resources.

```cpp
// Old style — universal but cannot steal
void sink(const std::string& s) { data_ = s; }  // always copies

// New style — only accepts rvalues, can move
void sink(std::string&& s) { data_ = std::move(s); } // zero-copy transfer
```

## Overload Resolution with && vs &

When both overloads exist, the compiler picks the best match:

```cpp
void f(std::vector<int>& v)  { std::cout << "lvalue\n"; }
void f(std::vector<int>&& v) { std::cout << "rvalue\n"; }

std::vector<int> v{1, 2, 3};
f(v);                        // prints: lvalue
f(std::vector<int>{4, 5, 6}); // prints: rvalue  (prvalue)
f(std::move(v));             // prints: rvalue  (xvalue)
```

## Rvalue References Enable "Stealing"

The power comes from being able to transfer ownership of heap-allocated resources without copying:

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    // Move constructor — steal the other object's pointer
    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_)
    {
        other.data_ = nullptr;  // leave source in valid state
        other.size_ = 0;
    }
};
```

An rvalue reference parameter tells the compiler: "the caller no longer needs this object after this call." You can plunder its internals as long as you leave it in a *valid but unspecified* state.

## Named rvalue References Are lvalues — Revisited

This is important enough to repeat with a concrete example:

```cpp
Buffer make_buffer();

void process(Buffer&& b) {
    // 'b' is a named rvalue reference parameter.
    // Inside this scope, 'b' is an LVALUE.
    Buffer local = b;           // COPY — b still intact
    Buffer local2 = std::move(b); // MOVE — b is emptied
}
```

The moment you give an rvalue reference a name, it becomes an lvalue. You must use `std::move` to re-cast it to an rvalue when forwarding it deeper.

## Rvalue References vs Forwarding References

Both use `&&` syntax, but they are different things:

| Syntax | Context | Name |
|--------|---------|------|
| `T&&` where `T` is a concrete type | Function parameter | Rvalue reference |
| `T&&` where `T` is a deduced template param | Template function | Forwarding reference |

```cpp
void sink(std::string&& s);    // rvalue reference — only rvalues
template<typename T>
void relay(T&& t);             // forwarding reference — lvalues AND rvalues
```

Forwarding references are covered in the perfect forwarding lesson.

## Common Pitfall: Returning rvalue References

Never return an rvalue reference to a local variable:

```cpp
std::string&& bad() {
    std::string s = "oops";
    return std::move(s); // DANGLING reference — s is destroyed on return
}

std::string good() {
    std::string s = "ok";
    return s; // NRVO or implicit move — correct
}
```

> **Interview answer:** An rvalue reference (`T&&`) binds exclusively to temporaries or explicitly moved-from objects, enabling the compiler to call move-optimized overloads that steal resources instead of copying them. Inside a function, a named rvalue reference parameter is itself an lvalue and must be re-cast with `std::move` to forward it as an rvalue.
