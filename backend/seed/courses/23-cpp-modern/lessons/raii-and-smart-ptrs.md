# RAII and Smart Pointers

**RAII** — Resource Acquisition Is Initialization — is the most important idea in C++. A resource (memory, file, lock, socket) is **tied to an object's lifetime**: acquire in the constructor, release in the destructor. When the object goes out of scope, the destructor runs deterministically — no GC, no leaks, no forgotten cleanup.

## The pattern

```cpp
{
    std::ofstream f("data.txt");   // acquired
    f << "hello";
}                                   // destructor closes file
```

You don't `f.close()`. The destructor does. Exception thrown? Still runs. Early return? Still runs. RAII is leak-resistant by construction.

## std::unique_ptr

The default smart pointer. Owns its pointee; cannot be copied; can be moved.

```cpp
#include <memory>

auto p = std::make_unique<User>(1, "Alice");
p->name;
*p = User{2, "Bob"};                 // assignment via deref

std::unique_ptr<User> p2 = std::move(p);    // ownership transferred
// p is now nullptr; p2 owns the User
```

When `p2` goes out of scope, the `User` is deleted. No `delete` needed anywhere in your code.

Use `unique_ptr` for **single-owner** dynamic objects:

```cpp
class Server {
    std::unique_ptr<Database> db_;
public:
    Server() : db_(std::make_unique<Database>("localhost")) {}
    // no destructor needed; ~Server() runs ~unique_ptr<Database>() runs ~Database()
};
```

## std::shared_ptr

Reference-counted. Multiple shared_ptrs can co-own the same object; the last one deletes it.

```cpp
auto p = std::make_shared<User>(1, "Alice");
auto p2 = p;        // refcount = 2
p.reset();          // refcount = 1
p2.reset();         // refcount = 0; User deleted
```

Cost: an extra heap allocation for the control block, atomic refcount updates. Use only when ownership is **genuinely shared** — most cases want `unique_ptr`.

### Cycles

Two `shared_ptr`s pointing at each other form a cycle and never free. Break with `std::weak_ptr`:

```cpp
struct Node {
    std::shared_ptr<Node> child;
    std::weak_ptr<Node> parent;
};
```

## Why not raw pointers?

Raw `new`/`delete` is error-prone:

```cpp
User* u = new User(1, "Alice");
if (something()) return;     // ❌ leak
delete u;
```

Smart pointers make this case impossible — the destructor runs no matter how you exit.

## RAII for non-memory resources

Anything that needs cleanup pairs perfectly with RAII:

```cpp
{
    std::lock_guard<std::mutex> lock(mutex_);   // locks
    // critical section
}                                                // unlocks automatically

{
    std::unique_lock<std::mutex> lock(mutex_, std::defer_lock);
    lock.lock();
    // ...
}
```

`lock_guard`, `unique_lock`, `scoped_lock` for mutexes. `std::fstream` for files. `std::shared_ptr<Connection>` for database connections. The pattern is universal.

## Custom RAII wrappers

```cpp
struct FileCloser {
    FILE* f;
    ~FileCloser() { if (f) fclose(f); }
};
```

Or, for legacy C APIs, `std::unique_ptr` with a custom deleter:

```cpp
auto file = std::unique_ptr<FILE, decltype(&fclose)>(fopen("x", "r"), fclose);
```

## std::scoped_lock and structured bindings

```cpp
std::scoped_lock lock(mtx_a, mtx_b);    // locks both, deadlock-free
auto [it, inserted] = map.emplace(k, v);
```

## The single most important rule

**Don't write `new` or `delete` in modern C++.** Use `make_unique`, `make_shared`, or stack allocation. The few exceptions (writing a smart pointer; talking to a C API) are rare and well-marked.
