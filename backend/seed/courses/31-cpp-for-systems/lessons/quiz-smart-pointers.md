# Quiz: Smart Pointers

**Q1. Which statement about `std::unique_ptr` is correct?**

- [ ] It can be copied, but copying increments an internal reference count.
- [x] It can be moved but not copied, enforcing exclusive ownership.
- [ ] It stores a reference count in a separate heap-allocated control block.
- [ ] It calls `free()` on the managed pointer by default.

_`unique_ptr` is a move-only type. Copying is deleted at compile time to ensure exactly one owner at all times. It calls `delete` (or a custom deleter), not `free()`._

---

**Q2. What is the primary advantage of `std::make_shared<T>()` over `std::shared_ptr<T>(new T())`?**

- [ ] `make_shared` allows a custom deleter to be specified.
- [ ] `make_shared` produces a `unique_ptr` that can be implicitly converted.
- [x] `make_shared` performs a single heap allocation for both the object and the control block.
- [ ] `make_shared` skips the control block entirely, reducing overhead.

_`make_shared` co-locates the managed object and the control block in one allocation, improving cache locality and reducing allocator overhead. The two-argument form (`shared_ptr<T>(new T())`) requires two separate allocations._

---

**Q3. Given this code, what is printed?**

```cpp
struct Node { std::shared_ptr<Node> next; ~Node(){ std::cout<<"D"; } };
auto a = std::make_shared<Node>();
auto b = std::make_shared<Node>();
a->next = b;
b->next = a;
```

- [ ] `DD` — both destructors run when `a` and `b` go out of scope.
- [ ] `D` — only one destructor runs.
- [x] (nothing) — both nodes leak because of a reference cycle.
- [ ] The program crashes with a double-free.

_`a` holds a `shared_ptr` to `b`, and `b` holds a `shared_ptr` to `a`. When the local handles go out of scope, each node still has a strong count of 1 held by the other. Neither is ever destroyed. Replacing one direction with `weak_ptr` breaks the cycle._

---

**Q4. Which is the correct way to safely access an object through a `std::weak_ptr`?**

- [ ] `if (!wp.expired()) { wp->doWork(); }`
- [x] `if (auto sp = wp.lock()) { sp->doWork(); }`
- [ ] `*wp.get();`
- [ ] `wp->doWork();`

_`weak_ptr` cannot be dereferenced directly. `lock()` atomically checks the strong count and, if non-zero, returns a valid `shared_ptr`. Using `expired()` followed by a separate `lock()` creates a time-of-check/time-of-use race — the object could be destroyed between the two calls._

---

**Q5. When does `std::shared_ptr`'s control block get freed?**

- [ ] When the managed object's destructor runs.
- [ ] When the last `shared_ptr` to the object is destroyed.
- [x] When both the last `shared_ptr` AND the last `weak_ptr` to the object are destroyed.
- [ ] Immediately when `use_count()` drops to 1.

_The control block holds two counts: `strong_count` (owners) and `weak_count` (observers plus an implicit +1 while strong_count > 0). The managed object is destroyed when `strong_count` hits 0, but the control block itself is freed only when `weak_count` also hits 0._

---

**Q6. Which raw pointer usage is correct and idiomatic in modern C++?**

- [ ] `Widget* w = new Widget(); processAll(w);` — raw owning pointer passed around.
- [ ] `auto sp = std::make_shared<Widget>(); Widget* w = sp.get(); sp.reset(); w->run();` — using raw pointer after `shared_ptr` reset.
- [x] `auto owner = std::make_unique<Widget>(); helper(owner.get());` — passing a non-owning raw pointer to a helper that uses it only within the call.
- [ ] `Widget* arr[10]; for(auto& p : arr) p = new Widget();` — raw array of owning pointers.

_A raw pointer returned by `.get()` is a non-owning borrow. It is correct as long as the borrow does not outlive the `unique_ptr`. The helper receives access without ownership, which is the intended pattern for short-lived observation._
