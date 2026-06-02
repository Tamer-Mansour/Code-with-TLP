# Nested Classes and Member Layout

C++ allows classes to be defined inside other classes (**nested classes**) and even inside functions (**local classes**). Understanding how members are laid out in memory is equally important for systems work where ABI compatibility, cache efficiency, and hardware alignment matter.

## Nested Classes

A nested class is a type declaration inside another class body. It is primarily a **namespace scoping** tool — the inner class name is qualified by the outer class name.

```cpp
class LinkedList {
public:
    class Iterator {            // nested class — scoped to LinkedList
    public:
        Iterator(Node* n) : current_(n) {}
        int  operator*()  const { return current_->value; }
        void operator++()       { current_ = current_->next; }
        bool operator!=(const Iterator& o) const { return current_ != o.current_; }
    private:
        Node* current_;
    };

    Iterator begin() { return Iterator(head_); }
    Iterator end()   { return Iterator(nullptr); }

private:
    struct Node {               // nested struct — the list node
        int   value;
        Node* next = nullptr;
    };
    Node* head_ = nullptr;
};

LinkedList list;
// ...
for (auto it = list.begin(); it != list.end(); ++it)
    printf("%d\n", *it);
```

Key rules for nested classes:

- The nested class is **not** automatically a friend of the outer class — it obeys normal access rules.
- The outer class is **not** a friend of the nested class either.
- To give the nested class access to the outer class's private members, declare it a `friend`.

```cpp
class Outer {
    friend class Outer::Inner;  // explicitly grant friendship
    int secret_ = 42;

    class Inner {
        void peek(Outer& o) { printf("%d\n", o.secret_); }  // OK after friend
    };
};
```

## Local Classes (Inside Functions)

A class defined inside a function body is a **local class**. It is invisible outside the function and cannot have static data members.

```cpp
void processData(int* arr, int n) {
    class Sorter {               // local class
    public:
        static void sort(int* a, int sz) {
            // simple bubble sort for demo
            for (int i = 0; i < sz - 1; ++i)
                for (int j = 0; j < sz - i - 1; ++j)
                    if (a[j] > a[j+1]) std::swap(a[j], a[j+1]);
        }
    };
    Sorter::sort(arr, n);
}
```

Local classes are useful for one-off helpers or callbacks defined close to their use — they were important before lambdas existed.

## Member Memory Layout

The compiler lays out data members **in declaration order**. Padding bytes may be inserted to satisfy alignment requirements.

```cpp
struct Example {
    char   a;       // 1 byte, offset 0
    // 3 bytes padding (to align int to 4-byte boundary)
    int    b;       // 4 bytes, offset 4
    char   c;       // 1 byte, offset 8
    // 3 bytes padding (to reach 4-byte total multiple)
};
// sizeof(Example) == 12 on most platforms
```

### Reducing Padding: Sort by Decreasing Size

```cpp
struct Packed {
    int    b;       // 4 bytes, offset 0
    char   a;       // 1 byte,  offset 4
    char   c;       // 1 byte,  offset 5
    // 2 bytes padding
};
// sizeof(Packed) == 8 — saves 4 bytes over Example
```

### Verifying Layout

```cpp
#include <cstddef>
static_assert(offsetof(Packed, b) == 0);
static_assert(offsetof(Packed, a) == 4);
```

## `#pragma pack` and `__attribute__((packed))`

For hardware structures (protocol headers, register maps) that must match an exact binary layout, packing removes padding entirely:

```cpp
#pragma pack(push, 1)
struct EthernetHeader {
    uint8_t  dst_mac[6];
    uint8_t  src_mac[6];
    uint16_t ether_type;
};  // sizeof == 14, no padding
#pragma pack(pop)
```

Packed structs may cause unaligned accesses on strict-alignment architectures (e.g., ARM without unaligned-access support) — use with care.

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Nested class | Type scoped inside another type; not automatically a friend |
| Local class | Type scoped inside a function; cannot have static members |
| Member layout | Declaration order; padding for alignment |
| `offsetof` | Reports byte offset of a member within a struct |
| `#pragma pack(1)` | Removes padding; may cause unaligned accesses |

---

> **Interview answer:** "A nested class is a type declared inside another class, scoped under the outer class name. Member layout follows declaration order with alignment padding inserted by the compiler. For hardware structures you can suppress padding with `#pragma pack`, but this risks unaligned accesses on strict-alignment architectures."
