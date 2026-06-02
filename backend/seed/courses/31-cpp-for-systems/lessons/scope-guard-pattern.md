# The Scope Guard Pattern

Sometimes you cannot easily wrap a resource in a dedicated class — the cleanup action is one-off, ad hoc, or involves complex state that would be cumbersome to encapsulate. The **scope guard** pattern solves this by letting you register an arbitrary cleanup callable that executes when the scope exits, whether normally or via exception.

## The Core Idea

A scope guard is a small RAII object that holds a callable (lambda, function pointer, or `std::function`) and invokes it in its destructor.

```cpp
template<typename F>
class ScopeGuard {
public:
    explicit ScopeGuard(F&& fn) : fn_(std::forward<F>(fn)), active_(true) {}

    ~ScopeGuard() noexcept {
        if (active_) {
            try { fn_(); } catch (...) {}  // swallow — destructor must not throw
        }
    }

    // Dismiss if the operation succeeded and cleanup is not needed
    void dismiss() noexcept { active_ = false; }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

private:
    F fn_;
    bool active_;
};

// Deduction guide / factory (C++17)
template<typename F>
ScopeGuard<F> make_scope_guard(F&& fn) {
    return ScopeGuard<F>(std::forward<F>(fn));
}
```

## Usage: Unconditional Cleanup

```cpp
void write_file(const char* path, const void* data, size_t len) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1) throw std::system_error(errno, std::generic_category());

    auto guard = make_scope_guard([fd] { close(fd); });

    if (write(fd, data, len) != static_cast<ssize_t>(len))
        throw std::runtime_error("partial write");

    // Guard closes fd whether we throw or return normally
}
```

## Usage: Dismissible Guard (Commit Pattern)

The power of `dismiss()` is that you can register rollback as the default and commit only on success:

```cpp
void create_user(Database& db, const std::string& name) {
    db.begin_transaction();
    auto rollback = make_scope_guard([&db] { db.rollback(); });

    db.insert("users", name);
    db.insert("roles", name, "viewer");

    // All steps succeeded — commit and cancel the rollback
    db.commit();
    rollback.dismiss();
}
```

If any step throws, `rollback` is not dismissed and the destructor calls `db.rollback()`.

## C++17 / C++20 Alternatives

**`std::experimental::scope_exit`** (from the Library Fundamentals TS, shipping in `<scope>` in some toolchains):

```cpp
#include <scope>   // may require GCC 12+ or MSVC 17.4+

{
    auto guard = std::experimental::scope_exit([&] { cleanup(); });
    risky_operation();
}  // cleanup() called here
```

The TS defines three variants:

| Type | Executes when |
|---|---|
| `scope_exit` | Always on scope exit |
| `scope_fail` | Only if an exception is propagating |
| `scope_success` | Only if no exception is propagating |

## Macro-Based Scope Guard (C-style codebases)

Some codebases use a macro for ergonomics:

```cpp
#define SCOPE_EXIT(code) \
    auto _guard_##__LINE__ = make_scope_guard([&]{ code; })

void example() {
    int fd = open("f", O_RDONLY);
    SCOPE_EXIT(close(fd));
    // ...
}
```

This is convenient but makes it harder to call `dismiss()`. Prefer the named variable for anything that needs conditional dismissal.

## When to Use a Scope Guard vs. a Dedicated RAII Class

| Situation | Prefer |
|---|---|
| Reusable resource type (file, lock, socket) | Dedicated RAII class |
| One-off cleanup in a single function | Scope guard |
| Rollback logic tied to local variables | Scope guard with dismiss |
| The cleanup is a multi-step lambda | Scope guard |

## Common Pitfalls

- **Capturing by reference in a long-lived guard.** If the guard outlives the variables it captures, you have dangling references. Capture by value when in doubt.
- **Forgetting that the cleanup lambda must not throw.** Wrap the call in try/catch inside the destructor, or ensure the lambda is `noexcept`.
- **Accidental copy of the guard.** The copy constructor should be deleted to prevent multiple executions of the cleanup.

**Interview answer:** A scope guard is a RAII object that stores an arbitrary callable and executes it in its destructor, providing automatic cleanup for ad hoc resources or rollback logic without writing a dedicated wrapper class.
