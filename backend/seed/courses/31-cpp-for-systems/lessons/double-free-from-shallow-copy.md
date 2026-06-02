# How Shallow Copy Causes Double Free

A double free occurs when `delete` (or `delete[]` or `free`) is called on the same memory address more than once. It is undefined behaviour — in practice it corrupts the heap allocator's internal data structures and almost always causes a crash, silent memory corruption, or a security vulnerability.

## The Minimal Reproducing Example

```cpp
#include <cstring>

class MyString {
    char* buf_;
public:
    MyString(const char* s) {
        buf_ = new char[strlen(s) + 1];
        strcpy(buf_, s);
    }
    ~MyString() { delete[] buf_; }
    // No user-defined copy constructor or copy assignment
};

int main() {
    MyString a("hello");
    MyString b = a;       // compiler shallow-copies: b.buf_ == a.buf_
}   // ~MyString() for b: delete[] buf_  → first free
    // ~MyString() for a: delete[] buf_  → SECOND free of same address → UB
```

Both destructors fire on the **same pointer**. The heap is now corrupted.

## Tracing the Bug Step by Step

```
1. MyString a("hello")
   a.buf_ → 0x1000  ["hello\0"]

2. MyString b = a          (shallow copy — compiler generated)
   b.buf_ → 0x1000         ← same address as a.buf_

3. ~MyString() for b fires (b goes out of scope first)
   delete[] 0x1000          ← memory at 0x1000 is freed
   heap allocator marks 0x1000 as free

4. ~MyString() for a fires
   delete[] 0x1000          ← DOUBLE FREE
   heap allocator: 0x1000 already free → undefined behaviour
```

## Why UB Is Dangerous in Practice

The C++ standard says double free is undefined behaviour, which means anything can happen:

- **Immediate crash** via `SIGABRT` or `SIGSEGV` — the most common outcome with debug allocators or AddressSanitizer.
- **Silent heap corruption** — the allocator's free list is corrupted; subsequent `new` calls return garbage addresses.
- **Security exploit** — in systems code, heap metadata corruption can be turned into arbitrary code execution (heap-spray attacks).

## Detecting the Bug

Use AddressSanitizer (`-fsanitize=address`) to catch it instantly:

```bash
g++ -fsanitize=address -g bug.cpp -o bug && ./bug
```

Output:
```
=================================================================
==12345==ERROR: AddressSanitizer: heap-use-after-free
...
==12345==ERROR: AddressSanitizer: attempting double-free on 0x602000000010
```

Valgrind also reports this as "Invalid free() / delete / delete[]".

## The Fix: Deep Copy

```cpp
MyString(const MyString& other) {
    buf_ = new char[strlen(other.buf_) + 1];   // new allocation
    strcpy(buf_, other.buf_);                  // copy content
}

MyString& operator=(MyString rhs) {            // copy-and-swap
    using std::swap;
    swap(buf_, rhs.buf_);
    return *this;
}
```

Now `a.buf_` and `b.buf_` point to separate allocations. Each destructor frees its own memory exactly once.

## Common Scenarios Where This Hits You

| Scenario | Why shallow copy occurs |
|---|---|
| `std::vector<MyString>` resize | Elements are moved/copied; copy ctor is called |
| Returning object by value (without elision) | Copy constructor invoked on return |
| Passing object by value to a function | Copy constructor invoked for parameter |
| Storing objects in C-style arrays and memcpy-ing | Bypasses constructors entirely — even worse |

## The Role of the Rule of Three

The double-free bug is the canonical motivation for the Rule of Three:

- You wrote a **destructor** (`delete[] buf_`).
- Therefore you need a **copy constructor** (deep copy).
- Therefore you need a **copy assignment operator** (deep copy, releasing old resource).

If you forget any one of the three, resource aliasing or leaks result.

## Summary of Warning Signs

- A class with `new`/`malloc` in the constructor and no user-defined copy members.
- Crash only with multiple copies of an object, or only when objects go out of scope at the end of a block.
- "Double free or corruption" message from glibc, or `SIGABRT` at program exit.

> **Interview answer:** Shallow copy duplicates a pointer without allocating new storage, so two objects share the same heap block. When both destructors run, `delete` is called twice on the same address — double free — which is undefined behaviour and typically crashes or corrupts the heap. The fix is a deep-copying copy constructor and copy assignment operator.
