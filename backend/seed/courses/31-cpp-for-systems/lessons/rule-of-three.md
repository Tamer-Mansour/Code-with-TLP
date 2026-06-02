# The Rule of Three

The Rule of Three is a C++ guideline that states: if a class defines **any one** of the following three special member functions, it almost certainly needs to define **all three**:

1. **Destructor**
2. **Copy constructor**
3. **Copy assignment operator**

The reasoning is simple: if you need a custom destructor, it is because your class manages a resource (typically heap memory). If you manage a resource, the compiler-generated copy constructor and copy assignment operator will perform **shallow copies** of your owning pointer — aliasing the resource between two objects and causing a **double-free** when both are destroyed.

## The Pattern That Triggers the Rule

```cpp
class Buffer {
    int* data_;
    int  size_;
public:
    Buffer(int n) : size_(n), data_(new int[n]{}) {}
    ~Buffer() { delete[] data_; }   // <-- you wrote a destructor
};
```

Now consider what happens with the compiler-generated copies:

```cpp
void demo() {
    Buffer a(5);
    Buffer b = a;    // shallow copy: b.data_ == a.data_
}   // both destructors fire → double free → crash
```

## Completing the Three

```cpp
class Buffer {
    int* data_;
    int  size_;

    void copy_from(const Buffer& src) {
        size_ = src.size_;
        data_ = new int[src.size_];
        std::copy(src.data_, src.data_ + src.size_, data_);
    }

public:
    // 1. Constructor
    Buffer(int n) : size_(n), data_(new int[n]{}) {}

    // 2. Destructor
    ~Buffer() { delete[] data_; }

    // 3. Copy constructor
    Buffer(const Buffer& other) { copy_from(other); }

    // 4. Copy assignment operator
    Buffer& operator=(Buffer rhs) {    // copy-and-swap
        swap(*this, rhs);
        return *this;
    }

    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.size_, b.size_);
    }
};
```

All three special functions now exist, and the class is safe to copy and assign.

## Diagnostic: Which Member Did You Write?

| Member written | Missing members | Risk |
|---|---|---|
| Destructor only | Copy ctor, copy assign | Double-free, aliasing |
| Copy constructor only | Destructor, copy assign | Memory leak, shallow assign |
| Copy assign only | Destructor, copy ctor | Leak, unsafe construction copy |
| All three | — | Correct |

## The Rule in Practice

A quick heuristic: search your class for `new`, `malloc`, `fopen`, `socket`, or any other resource-acquisition call. If you find one, apply the Rule of Three.

Modern C++ (C++11 onward) extends this to the **Rule of Five** by adding:

- **Move constructor** `MyClass(MyClass&&)`
- **Move assignment operator** `MyClass& operator=(MyClass&&)`

These allow efficient transfer of resources without copying. However, the Rule of Three remains fully valid for C++03-era code and for classes that only need copy semantics.

## Enforcing with `= delete`

Sometimes copying a resource makes no sense (e.g., a mutex, a file handle). In that case, define the destructor and **delete** the copies:

```cpp
class FileHandle {
    FILE* fp_;
public:
    explicit FileHandle(const char* path) : fp_(fopen(path, "r")) {}
    ~FileHandle() { if (fp_) fclose(fp_); }

    FileHandle(const FileHandle&)            = delete;
    FileHandle& operator=(const FileHandle&) = delete;
};
```

Deleting the copy members is itself satisfying the Rule of Three — you are making an explicit, conscious decision about all three.

## Summary

- Write a destructor? Write a copy constructor and copy assignment operator too.
- The compiler-generated copies are **shallow** — safe only for classes without raw owning pointers.
- If copying is semantically wrong, `= delete` both copy members.

> **Interview answer:** The Rule of Three says: if you define a destructor (because you own a resource), you must also define the copy constructor and copy assignment operator; otherwise the compiler generates shallow copies that alias the resource, leading to double-free bugs when both objects are destroyed.
