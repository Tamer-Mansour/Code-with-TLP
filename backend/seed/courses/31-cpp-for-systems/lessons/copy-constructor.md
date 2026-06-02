# The Copy Constructor: When It Is Called

The copy constructor is a special constructor that creates a new object as a copy of an existing one. Understanding exactly when the compiler calls it — versus when it elides the call entirely — is essential for writing correct resource-managing classes.

## Signature

```cpp
class MyClass {
public:
    MyClass(const MyClass& other);   // copy constructor
};
```

The parameter is almost always a **const lvalue reference**. Passing by value would trigger an infinite recursive call (to copy the argument you need to call the copy constructor…). The `const` allows copying from temporaries bound to const references.

## When Is the Copy Constructor Called?

### 1. Direct copy initialisation

```cpp
MyClass a;
MyClass b = a;      // copy constructor
MyClass c(a);       // also copy constructor
```

### 2. Passing by value to a function

```cpp
void process(MyClass obj);   // obj is copy-constructed from the argument
process(a);                  // copy constructor called here
```

### 3. Returning by value from a function (without elision)

```cpp
MyClass make() {
    MyClass tmp;
    return tmp;   // may call copy constructor (but see copy elision)
}
MyClass x = make();
```

Modern compilers apply **Named Return Value Optimisation (NRVO)** or **copy elision** and often eliminate this call entirely.

### 4. Throwing and catching by value

```cpp
throw MyClass();          // copy constructor may be called
} catch (MyClass obj) {   // copy constructor from exception object to obj
```

## Writing a Deep-Copying Copy Constructor

For a class that owns a dynamic array:

```cpp
class Buffer {
    int* data_;
    int  size_;
public:
    // Ordinary constructor
    Buffer(int n) : size_(n), data_(new int[n]{}) {}

    // Copy constructor — deep copy
    Buffer(const Buffer& other)
        : size_(other.size_),
          data_(new int[other.size_])
    {
        std::copy(other.data_, other.data_ + other.size_, data_);
    }

    // Destructor
    ~Buffer() { delete[] data_; }
};
```

After the copy constructor runs, `data_` points to a **new allocation** containing the same integers — fully independent from `other`.

## Delegating to a Helper

A common pattern separates resource allocation into a private helper so the copy constructor and copy assignment operator share logic:

```cpp
class Buffer {
    void init(const Buffer& src) {
        size_ = src.size_;
        data_ = new int[src.size_];
        std::copy(src.data_, src.data_ + src.size_, data_);
    }
public:
    Buffer(const Buffer& other) { init(other); }
    // assignment will also call init after cleanup
};
```

## Common Pitfalls

- **Forgetting the copy constructor** when a destructor is defined. The compiler still generates one — performing a shallow memberwise copy — which aliases the pointer and causes a double-free.
- **Passing large objects by value** unexpectedly when you meant `const&`, causing a costly and unintended copy.
- **Copying in a loop**: each iteration invokes the copy constructor; prefer passing by reference or using move semantics where applicable.

## Checking Whether the Compiler Generates One

If you declare any constructor, the compiler still provides a copy constructor unless you explicitly `delete` or `=default` it:

```cpp
class NoCopy {
public:
    NoCopy(const NoCopy&) = delete;             // disable
    NoCopy& operator=(const NoCopy&) = delete;  // disable
};
```

Use `= delete` for resource handles (like `std::unique_ptr`) where copying makes no semantic sense.

## Quick Decision Table

| Class contains… | Action |
|---|---|
| Only value types / smart pointers | Accept compiler-generated copy constructor |
| Raw owning pointer | Write a deep-copying copy constructor |
| Non-copyable resource (mutex, socket) | `= delete` the copy constructor |

> **Interview answer:** The copy constructor is called when an object is copy-initialised, passed by value, or returned by value (absent elision). For classes owning raw pointers, you must write a deep-copying version; otherwise the compiler-generated shallow copy aliases the pointer and causes a double-free on destruction.
