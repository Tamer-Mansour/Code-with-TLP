# Why Move Operations Should Be noexcept

Marking move constructors and move assignment operators `noexcept` is not just a stylistic hint — it fundamentally changes how the standard library treats your type, with measurable performance consequences.

## The Strong Exception Guarantee

Standard library containers like `std::vector` provide the **strong exception guarantee**: if an operation throws, the container is left in its original, unmodified state. When `std::vector` grows (reallocates), it must move or copy every existing element to new storage.

The critical question: can it use move operations?

- If move is `noexcept`, the move cannot fail. The container can move all elements safely.
- If move might throw, a failure mid-reallocation would leave the container in a partially-modified state — violating the strong guarantee. So the container **falls back to copying**, which cannot invalidate the original.

## Demonstration

```cpp
#include <vector>
#include <iostream>

struct MovesMayThrow {
    int* data = new int(0);
    MovesMayThrow() = default;
    ~MovesMayThrow() { delete data; }
    MovesMayThrow(MovesMayThrow&& o) // no noexcept
        : data(o.data) { o.data = nullptr; }
    MovesMayThrow(const MovesMayThrow& o)
        : data(new int(*o.data)) {
        std::cout << "COPY\n"; // this fires during reallocation!
    }
};

struct MovesNoThrow {
    int* data = new int(0);
    MovesNoThrow() = default;
    ~MovesNoThrow() { delete data; }
    MovesNoThrow(MovesNoThrow&& o) noexcept // noexcept declared
        : data(o.data) { o.data = nullptr; }
    MovesNoThrow(const MovesNoThrow& o) : data(new int(*o.data)) {
        std::cout << "COPY\n"; // this should NOT fire
    }
};

int main() {
    std::vector<MovesMayThrow> v1;
    for (int i = 0; i < 5; ++i) v1.emplace_back(); // prints COPY on realloc

    std::vector<MovesNoThrow> v2;
    for (int i = 0; i < 5; ++i) v2.emplace_back(); // no COPY printed
}
```

Without `noexcept`, `std::vector` copies every element on every reallocation — O(n) copies per `push_back` that triggers growth.

## The Type Trait: is_nothrow_move_constructible

The standard library uses this trait at compile time to make the decision:

```cpp
#include <type_traits>

static_assert(std::is_nothrow_move_constructible_v<MovesNoThrow>);
// std::vector internally checks this trait before choosing move vs copy
```

You can verify your type will be moved (not copied) during reallocation:

```cpp
static_assert(std::is_nothrow_move_constructible_v<YourType>,
              "YourType will be copied during vector reallocation!");
```

## Which Operations to Mark noexcept

| Operation | noexcept? | Reason |
|-----------|-----------|--------|
| Move constructor | Yes (when possible) | Enables move in containers |
| Move assignment | Yes (when possible) | Enables move in containers |
| Destructor | Always (implicitly) | Compiler adds it automatically |
| `swap` | Yes | `std::swap` specializations rely on it |
| Copy constructor | Usually no | Allocation can fail |

## Can You Always Mark Move noexcept?

Not automatically — it depends on your members:

```cpp
struct Risky {
    std::vector<int> data_;  // std::vector move is noexcept
    std::mutex       mu_;    // std::mutex move is DELETED — cannot move

    // Would need careful design here
};
```

If any member's move constructor can throw, propagating `noexcept` would be a lie. Compilers will warn or give errors if you declare `noexcept` on a function that calls potentially-throwing operations.

Use `noexcept(noexcept(...))` for conditional propagation:

```cpp
MyType(MyType&& o) noexcept(noexcept(member_(std::move(o.member_))))
    : member_(std::move(o.member_)) {}
```

Or use `= default` — the compiler infers `noexcept` correctly when all members are nothrow-movable.

## Key Takeaway

```cpp
class GoodRAII {
    int*   data_;
    size_t size_;
public:
    GoodRAII(GoodRAII&& o) noexcept  // without noexcept: copies in vector
        : data_(o.data_), size_(o.size_) {
        o.data_ = nullptr;
        o.size_ = 0;
    }
    GoodRAII& operator=(GoodRAII&& o) noexcept { /* ... */ return *this; }
};
```

`noexcept` on move operations is not optional polish — it is the difference between O(1) moves and O(n) copies inside every standard container that holds your type.

> **Interview answer:** Standard containers like `std::vector` check `std::is_nothrow_move_constructible` to decide whether to move or copy elements during reallocation. Without `noexcept` on your move constructor, the container falls back to copying every element on each resize to preserve the strong exception guarantee — turning O(1) moves into O(n) copies.
