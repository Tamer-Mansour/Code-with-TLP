# Shallow Copy vs Deep Copy: What Is the Difference?

When you copy an object in C++, the runtime must decide what "copy" means for every data member. For primitive types like `int` or `double`, the answer is trivial: just duplicate the bits. For **pointer members**, the answer splits into two fundamentally different strategies, and choosing the wrong one is a classic source of crashes and memory corruption.

## What Is a Shallow Copy?

A shallow copy duplicates the **pointer value itself**, not the data it points to. After the copy, both the original and the copy hold a pointer to the **same heap allocation**.

```cpp
struct Buffer {
    int* data;
    int  size;
};

Buffer a;
a.size = 3;
a.data = new int[3]{1, 2, 3};

Buffer b = a;   // compiler-generated copy: shallow!
// b.data == a.data  — same address, same memory
```

Modifying `b.data[0]` also changes `a.data[0]`. Worse, when both objects are destroyed, `delete[]` is called **twice** on the same address — undefined behaviour (UB), almost always a crash.

## What Is a Deep Copy?

A deep copy allocates **fresh storage** and copies the pointed-to content into it. Each object owns its own independent resource.

```cpp
Buffer deep_copy(const Buffer& src) {
    Buffer dst;
    dst.size = src.size;
    dst.data = new int[src.size];          // new allocation
    std::copy(src.data, src.data + src.size, dst.data);  // copy contents
    return dst;
}
```

Now `dst.data` and `src.data` point to different memory with equal contents. Destroying one object does not affect the other.

## Side-by-Side Comparison

| Property | Shallow Copy | Deep Copy |
|---|---|---|
| Pointer value | Duplicated | New allocation |
| Pointed-to data | Shared | Independent copy |
| Modification isolation | No | Yes |
| Double-free risk | Yes | No |
| Cost | O(1) | O(n) |

## When Does Shallow Copy Happen?

The **compiler-generated copy constructor and copy assignment operator** perform memberwise shallow copies. This is perfectly fine when the class contains no raw pointers (or uses smart pointers that handle ownership). It becomes dangerous the moment you store a raw owning pointer.

```cpp
class Danger {
    char* buf_;
public:
    Danger(const char* s) {
        buf_ = new char[strlen(s) + 1];
        strcpy(buf_, s);
    }
    ~Danger() { delete[] buf_; }
    // No user-defined copy constructor → compiler generates shallow copy
};

Danger x("hello");
Danger y = x;    // y.buf_ == x.buf_
// Both destructors fire → double free → crash
```

## When Deep Copy Is Necessary

You need a deep copy any time your class **owns** a resource through a raw pointer:

- Dynamically allocated arrays (`new[]`)
- File handles or socket descriptors stored as pointers
- Linked lists, trees, or other heap-allocated node graphs

## The Link to the Rule of Three

Whenever you write a **destructor** that frees a resource, you almost certainly also need a user-defined **copy constructor** and **copy assignment operator** — otherwise the compiler's shallow memberwise copies will create aliasing and double-free bugs. This is the Rule of Three, covered in a later lesson.

## Practical Rule of Thumb

Prefer owning wrappers (`std::string`, `std::vector`, `std::unique_ptr`) over raw pointers. These types already implement deep copy (or deleted copy for `unique_ptr`), so the compiler-generated specials do the right thing automatically.

> **Interview answer:** A shallow copy duplicates a pointer's address so both objects share the same heap memory; a deep copy allocates new memory and copies the contents, giving each object independent ownership. Shallow copies of owning pointers cause double-free bugs on destruction.
