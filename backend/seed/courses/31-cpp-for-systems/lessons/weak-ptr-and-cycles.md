# weak_ptr and Breaking Reference Cycles

`std::weak_ptr<T>` is a non-owning observer of a `shared_ptr`-managed object. It does not increment the strong reference count and cannot keep the object alive — but it can safely detect whether the object still exists and temporarily acquire ownership to use it.

## The Problem: Reference Cycles

When two `shared_ptr`-managed objects hold `shared_ptr`s to each other, a cycle forms and neither object is ever destroyed:

```cpp
struct Node {
    std::shared_ptr<Node> next;
    ~Node() { std::cout << "~Node\n"; }
};

auto a = std::make_shared<Node>();
auto b = std::make_shared<Node>();
a->next = b;
b->next = a;
// a and b go out of scope — neither destructor is ever called!
// strong_count for each object: 1 (held by the other node)
// Memory leak.
```

Neither `a` nor `b` can be destroyed because each still holds a `shared_ptr` to the other, keeping the other's `strong_count` at 1.

## weak_ptr Breaks the Cycle

Replace one direction of the cycle with a `weak_ptr`:

```cpp
struct Node {
    std::weak_ptr<Node> next;   // observes, does not own
    ~Node() { std::cout << "~Node\n"; }
};

auto a = std::make_shared<Node>();
auto b = std::make_shared<Node>();
a->next = b;   // weak assignment — b's strong_count stays at 1
b->next = a;   // weak assignment — a's strong_count stays at 1
// When a and b go out of scope, both strong counts hit 0 -> both destroyed
```

## Locking a weak_ptr

A `weak_ptr` cannot be dereferenced directly. You must **lock** it to get a temporary `shared_ptr`:

```cpp
std::weak_ptr<Widget> weak = someSharedPtr;

// Safe pattern: check and use atomically
if (auto sp = weak.lock()) {
    sp->doWork();   // sp is a valid shared_ptr, object alive for this scope
} else {
    // object was destroyed, weak.lock() returns null shared_ptr
}
```

`lock()` is atomic: it atomically checks whether `strong_count > 0` and, if so, increments it. There is no race between the check and the increment.

## expired() vs lock()

```cpp
weak.expired()      // true if strong_count == 0
weak.lock()         // returns shared_ptr (null if expired)
```

Never write `if (!weak.expired()) { auto sp = weak.lock(); sp->use(); }` — the object could be destroyed between `expired()` and `lock()`. Always use `lock()` directly.

## Observer Pattern: A Classic Use Case

```cpp
class EventSource {
    std::vector<std::weak_ptr<Listener>> listeners_;
public:
    void subscribe(std::shared_ptr<Listener> l) {
        listeners_.push_back(l);   // weak — EventSource does not own listeners
    }
    void notify() {
        // Clean up expired listeners while notifying
        std::erase_if(listeners_, [](const std::weak_ptr<Listener>& w) {
            if (auto l = w.lock()) {
                l->onEvent();
                return false;
            }
            return true;  // expired, remove from list
        });
    }
};
```

This pattern allows listeners to unsubscribe simply by going out of scope — no explicit unsubscribe call needed.

## Parent-Child Relationships

Tree data structures commonly have:
- Parent holds `shared_ptr<Child>` — parent owns children.
- Child holds `weak_ptr<Parent>` — child does not own parent.

```cpp
struct TreeNode {
    std::vector<std::shared_ptr<TreeNode>> children;
    std::weak_ptr<TreeNode> parent;  // back-reference
};
```

If child held a `shared_ptr<Parent>`, and parent a `shared_ptr<Child>`, neither could ever be destroyed.

## Costs of weak_ptr

- Size: two pointers (same as `shared_ptr`).
- `lock()` performs one atomic operation.
- The control block is kept alive (but not the object) until all `weak_ptr`s are gone.

## Common Pitfalls

- Using `expired()` for control flow instead of `lock()` — creates a TOCTOU race.
- Forgetting that `weak_ptr` cannot be created from a raw pointer — it must be created from a `shared_ptr` or another `weak_ptr`.
- Not realizing that `weak_count` being nonzero keeps the **control block** (not the object) alive.

## Interview Answer

**"When do you use weak_ptr?"**

> `weak_ptr` breaks `shared_ptr` reference cycles and implements non-owning observers that need to safely detect when the observed object has been destroyed. It does not affect the strong reference count, so it cannot cause leaks or extend object lifetimes.
