# static Local Variables and Their Lifetime

A local variable declared `static` inside a function is fundamentally different from a normal local: it lives for the entire duration of the program, not just the duration of the function call.

## Lifetime and Storage

Normal locals live on the stack — they are created on entry and destroyed on exit. A `static` local lives in the program's BSS or data segment:

```cpp
void count_calls() {
    static int count = 0;  // initialized exactly once, at first call
    ++count;
    printf("Called %d times\n", count);
}

count_calls();  // Called 1 times
count_calls();  // Called 2 times
count_calls();  // Called 3 times
```

The variable `count` persists across calls and retains its value.

## Initialization Guarantees (C++11 and Later)

C++11 mandates that `static` local initialization is **thread-safe**. The runtime inserts a hidden flag; if two threads race to call the function for the first time, only one performs the initialization and the other waits.

```cpp
Logger& get_logger() {
    static Logger instance;  // thread-safe, initialized once
    return instance;
}
```

This pattern is the canonical C++ **Meyers Singleton** — lazy, thread-safe, and automatically destroyed at program exit (in reverse construction order).

## Zero-Initialization for Trivial Types

If the initializer is absent, trivial `static` locals (integers, pointers) are zero-initialized before the program starts:

```cpp
void foo() {
    static int x;   // x == 0, guaranteed
}
```

## Practical Use Cases in Systems Code

**Stateful callbacks without global state:**
```cpp
// ISR uses a static buffer — no heap allocation
void uart_isr() {
    static char buf[64];
    static int  idx = 0;
    buf[idx++] = read_uart_byte();
    if (idx == sizeof(buf)) idx = 0;
}
```

**Lazy initialization of expensive objects:**
```cpp
const LookupTable& get_crc_table() {
    static LookupTable table = build_crc_table();  // built once, reused forever
    return table;
}
```

**Call-once setup:**
```cpp
bool hardware_init_done() {
    static bool done = (init_hardware(), true);
    return done;
}
```

## Common Pitfalls

- **Not thread-safe before C++11.** On pre-C++11 compilers or with `-fno-threadsafe-statics`, initialization races are possible. Embedded bare-metal targets may disable thread-safe statics to avoid the overhead.
- **Hidden global state.** `static` locals are effectively global variables scoped to a function — they make unit testing harder and can introduce subtle order-of-initialization bugs.
- **Destructor order.** Static locals are destroyed in reverse order of construction at program exit. Interleaving between translation units can cause crashes if one destructor depends on another already-destroyed static.

## Scope vs Lifetime

It is important to distinguish:

| Property | Normal local | static local |
|---|---|---|
| Scope (visibility) | Function body | Function body |
| Lifetime | Function call | Program lifetime |
| Storage | Stack | Static segment |
| Init threads | N/A | Thread-safe (C++11+) |

The scope is still the function — no external code can name the `static` local directly. Only the lifetime changes.

> **Interview answer:** "A `static` local variable is initialized exactly once (thread-safely in C++11+), retains its value between calls, and lives until the program exits, even though it is only visible inside the function."
