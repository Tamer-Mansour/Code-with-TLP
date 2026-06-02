# Inside shared_ptr: The Control Block

Understanding `shared_ptr`'s internal layout explains its cost model, its thread safety guarantees, and why `make_shared` is almost always better than constructing from a raw pointer.

## The Two Pointers Inside shared_ptr

Every `shared_ptr` instance stores two raw pointers:

1. **Pointer to the managed object** — what `get()` returns.
2. **Pointer to the control block** — a heap-allocated structure shared by all `shared_ptr` and `weak_ptr` instances that refer to the same object.

```
shared_ptr<Widget> p
┌───────────────────────┐
│  T* ptr_              │──────────────────────► Widget object
│  ControlBlock* ctrl_  │──────┐
└───────────────────────┘      │
                               ▼
                    ┌─────────────────────┐
                    │  strong_count  (2)  │  atomic
                    │  weak_count    (1)  │  atomic
                    │  deleter            │
                    │  allocator          │
                    └─────────────────────┘
```

This is why `sizeof(shared_ptr<T>)` is typically 16 bytes (two pointers on 64-bit systems) regardless of `T`.

## The Control Block Fields

| Field | Purpose |
|-------|---------|
| `strong_count` | How many `shared_ptr` instances share ownership. Object is destroyed when this reaches 0. |
| `weak_count` | How many `weak_ptr` instances observe this object, plus 1 if `strong_count > 0`. Control block is freed when this reaches 0. |
| Deleter | Callable used to destroy the object (defaults to `delete`). |
| Allocator | How to free the control block itself. |

The object and the control block have **independent lifetimes**: the object is destroyed when `strong_count` hits 0, but the control block lives until `weak_count` also hits 0.

## make_shared vs new: One Allocation vs Two

```cpp
// Two allocations: one for Widget, one for ControlBlock
std::shared_ptr<Widget> p(new Widget(args));

// One allocation: Widget and ControlBlock in a single contiguous block
auto p = std::make_shared<Widget>(args);
```

With `make_shared`, the layout looks like this:

```
┌──────────────────────────────────┐
│ strong_count │ weak_count │ ...  │  ← ControlBlock
│──────────────────────────────────│
│          Widget data             │  ← T storage
└──────────────────────────────────┘
```

Benefits of the single allocation:
- Faster (one `malloc`/`new` instead of two).
- Better cache locality — the control block and the object are adjacent.
- Fewer total bytes allocated.

Downside: the single allocation means the memory for the `Widget` itself cannot be freed until `weak_count` also drops to 0, even after the `Widget` is destroyed. If `weak_ptr` instances outlive all `shared_ptr` instances, the `Widget`'s memory stays allocated (though the `Widget` has been destroyed). With the two-allocation path, the `Widget`'s memory is freed as soon as `strong_count` hits 0.

## Atomic Reference Counting

Both `strong_count` and `weak_count` are atomic integers. Operations on them use `memory_order_acq_rel` semantics to ensure that the destructor of the managed object sees all writes performed by any thread that held a `shared_ptr`.

This makes copies and destructions of `shared_ptr` safe from multiple threads — but adds measurable cost on multi-core machines where the cache line containing the counts is heavily contested.

## enable_shared_from_this

Sometimes a class needs to produce a `shared_ptr` to itself (e.g., to pass `this` into an async callback):

```cpp
class Widget : public std::enable_shared_from_this<Widget> {
public:
    void startAsync() {
        auto self = shared_from_this();  // safe — increments strong_count
        async_op([self]{ self->onDone(); });
    }
};
```

`enable_shared_from_this` works by storing a `weak_ptr` to `this` inside the object when the first `shared_ptr` to it is created. `shared_from_this()` locks that `weak_ptr`. Calling `shared_from_this()` before a `shared_ptr` exists throws `std::bad_weak_ptr`.

## What Happens at Destruction

When the last `shared_ptr` is destroyed:
1. `strong_count` atomically decrements to 0.
2. The deleter is called — typically `delete ptr_` — destroying the managed object.
3. `weak_count` decrements by 1 (the implicit +1 held while `strong_count > 0`).
4. If `weak_count` is now also 0, the control block is freed.

When the last `weak_ptr` is destroyed (after all `shared_ptr` are gone):
- `weak_count` hits 0, control block is freed. Object was already destroyed in step 2 above.

## Interview Answer

**"Why is make_shared preferred over shared_ptr(new T)?"**

> `make_shared` performs a single allocation that co-locates the object and its control block, saving a heap allocation and improving cache locality. It is also more exception-safe because the object and the reference count are set up atomically in one step.
