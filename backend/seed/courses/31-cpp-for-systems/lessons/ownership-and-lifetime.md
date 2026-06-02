# Ownership, Lifetime, and Who Frees What

Every resource in a C++ program has exactly one owner at any given time. Ownership is the obligation to release a resource when it is no longer needed. Getting ownership semantics wrong — doubly owning, not owning, or losing track of ownership — is the root cause of double-frees, use-after-free bugs, and leaks.

## Ownership Vocabulary

| Term | Meaning |
|---|---|
| **Owner** | The entity responsible for releasing the resource |
| **Borrower** | Uses the resource without owning it — must not outlive the owner |
| **Transfer** | Moving ownership from one entity to another (via move semantics) |
| **Shared ownership** | Multiple owners; resource released when the last owner relinquishes it |

## Single Ownership: `std::unique_ptr`

`std::unique_ptr<T>` models exclusive ownership. There is exactly one owner; when it is destroyed, the resource is released.

```cpp
// Factory returns ownership to the caller
std::unique_ptr<Socket> create_connection(const char* host, int port) {
    auto sock = std::make_unique<Socket>(host, port);
    sock->set_timeout(5000);
    return sock;   // ownership transferred out (RVO / move)
}

void use_connection() {
    auto conn = create_connection("example.com", 443);
    conn->send("GET / HTTP/1.1\r\n");
    // conn destroyed here — socket closed
}
```

Ownership transfer via move:

```cpp
std::unique_ptr<File> file = open_log("/var/log/app.log");
Logger logger(std::move(file));   // file is now null; logger owns the File
```

After `std::move`, `file` is in a valid but empty state — do not use it.

## Borrowing: Raw Pointers and References as Non-Owning Views

A raw pointer or reference used as a function parameter signals: "I am borrowing this; I do not own it." The callee must not store it beyond the call unless the lifetime is guaranteed.

```cpp
// Takes a non-owning view — caller retains ownership
void log_error(const Socket& sock, const std::string& msg);

void process(std::unique_ptr<Socket>& conn) {
    log_error(*conn, "timeout");   // conn still owns the socket after this call
}
```

The key rule: **a borrower must never outlive the owner.**

```cpp
// BUG: storing a raw pointer beyond the owner's lifetime
int* dangling = nullptr;
{
    int x = 42;
    dangling = &x;
}          // x destroyed here
*dangling; // undefined behavior — use-after-free
```

## Shared Ownership: `std::shared_ptr`

When multiple independent owners must share a resource and the release should happen when the last one is done, use `std::shared_ptr`. It maintains a reference count.

```cpp
auto buffer = std::make_shared<Buffer>(4096);
auto writer = std::make_shared<Writer>(buffer);   // both hold a reference
auto reader = std::make_shared<Reader>(buffer);   // three owners

// When all three are destroyed, buffer is released
```

Pitfall: **cyclic references** prevent the count from reaching zero, causing a leak:

```cpp
struct Node {
    std::shared_ptr<Node> next;  // cycle: A→B→A — neither is ever freed
};
```

Break cycles with `std::weak_ptr`:

```cpp
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;    // non-owning back-link
};
```

## Lifetime Rules for System Code

1. **Resources live exactly as long as their owner.** Design owner lifetimes to match resource lifetimes.
2. **Move, don't copy, ownership.** Copying an owning object requires either deep-copying the resource or sharing it — make this decision explicit.
3. **Factory functions return `unique_ptr`.** Callers decide whether to keep exclusive ownership or convert to `shared_ptr`.
4. **APIs that borrow should accept references or raw pointers** — never `unique_ptr` by value (that would transfer ownership into the function).
5. **Avoid returning raw pointers from factories.** The caller has no way to know whether they own the result.

## Comparing Smart Pointer Types

| | `unique_ptr` | `shared_ptr` | `weak_ptr` |
|---|---|---|---|
| Ownership | Exclusive | Shared | None (observer) |
| Overhead | Zero | Atomic ref count | Shared control block |
| Copy | Deleted | Allowed | Allowed |
| Use when | Default choice | Multiple owners needed | Breaking cycles |

## Detecting Ownership Confusion

- **Double free:** two `unique_ptr`s initialized with the same raw pointer.
- **Use-after-move:** accessing a `unique_ptr` after `std::move`.
- **Leaked `shared_ptr` cycle:** use a memory profiler or `std::weak_ptr` for back-edges.
- **Dangling reference:** a borrowed reference outliving the owning object.

**Interview answer:** Ownership is the obligation to release a resource. In C++, `std::unique_ptr` models exclusive ownership, `std::shared_ptr` models shared ownership, and raw pointers/references model non-owning borrows — the caller must ensure the borrow does not outlive the owner.
