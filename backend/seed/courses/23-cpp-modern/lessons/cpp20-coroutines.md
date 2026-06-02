# C++20 Coroutines

Coroutines are functions that can be **suspended and resumed**. They enable writing asynchronous, lazy, or generator-style code that looks sequential — no callbacks, no state machines.

## The Three Magic Keywords

C++20 adds three new keywords that make a function a coroutine:

| Keyword | Effect |
|---------|--------|
| `co_return` | Finishes the coroutine and optionally returns a value |
| `co_yield expr` | Suspends, yields `expr` to the caller, then resumes |
| `co_await expr` | Suspends until `expr`'s awaitable is ready |

A function containing any of these keywords is automatically a coroutine.

## Generator Pattern with co_yield

The most approachable use case: a lazy sequence generator.

```cpp
#include <coroutine>
#include <optional>

// A minimal Generator<T> type (the standard library does not provide one in C++20;
// C++23 adds std::generator)
template<typename T>
struct Generator {
    struct promise_type {
        T current_value;
        auto get_return_object() { return Generator{this}; }
        auto initial_suspend() { return std::suspend_always{}; }
        auto final_suspend() noexcept { return std::suspend_always{}; }
        auto yield_value(T v) {
            current_value = v;
            return std::suspend_always{};
        }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    using handle_t = std::coroutine_handle<promise_type>;

    handle_t handle;
    explicit Generator(promise_type* p) : handle(handle_t::from_promise(*p)) {}
    ~Generator() { if (handle) handle.destroy(); }

    bool next() {
        handle.resume();
        return !handle.done();
    }
    T value() { return handle.promise().current_value; }
};

Generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        auto next = a + b;
        a = b;
        b = next;
    }
}

int main() {
    auto fib = fibonacci();
    for (int i = 0; i < 10 && fib.next(); ++i)
        std::cout << fib.value() << " ";
    // 0 1 1 2 3 5 8 13 21 34
}
```

The key insight: `fibonacci()` returns immediately. Each call to `fib.next()` runs the coroutine until the next `co_yield`, then suspends again. The infinite loop never blocks.

## C++23: std::generator

C++23 ships `std::generator<T>` so you don't need to write the boilerplate above:

```cpp
#include <generator>

std::generator<int> range(int start, int end) {
    for (int i = start; i < end; ++i)
        co_yield i;
}

for (int x : range(1, 6))
    std::cout << x << " ";   // 1 2 3 4 5
```

## Async Coroutines with co_await

The other major use case is async I/O. Frameworks like **Asio** (Boost.Asio / standalone Asio) provide awaitables:

```cpp
// Pseudo-code using Asio coroutines (requires asio library)
asio::awaitable<std::string> fetchPage(std::string host) {
    auto socket = co_await asyncConnect(host, 80);
    co_await asyncWrite(socket, "GET / HTTP/1.0\r\n\r\n");
    auto response = co_await asyncReadAll(socket);
    co_return response;
}
```

This reads like synchronous code but suspends the coroutine at each `co_await`, freeing the thread to do other work until the I/O completes.

## How Coroutines Work Under the Hood

1. The compiler transforms a coroutine into a **heap-allocated frame** containing local variables and a resume pointer.
2. `co_await` calls `suspend_ready()`, `suspend_awaiting()`, and `resume()` on an *awaitable* object.
3. The **promise object** (embedded in the frame) controls the return object and value delivery.

You rarely implement these primitives directly — library types (`std::generator`, Asio awaitables, cppcoro) do it for you.

## When to Use Coroutines

- **Lazy sequences** where computing all values upfront is too expensive or impossible (infinite sequences).
- **Async I/O** in network servers — write async code without callback hell.
- **Pipelines** — chain coroutines to pass data between stages without buffering.

Avoid coroutines for simple synchronous utility functions — the overhead and complexity are not justified.
