# Object Lifetime, Scope, and Destruction Order

In C++, *scope* (where a name is visible) and *lifetime* (when an object exists in memory) are related but distinct. Understanding the difference — and the precise destruction order — is essential for writing correct, resource-safe code.

## Scope vs Lifetime

- **Scope** is a compile-time concept: the region of source code where a name can be looked up.
- **Lifetime** is a runtime concept: the period during which an object's storage is allocated and the object is in a valid state.

For automatic variables they usually coincide, but not always:

```cpp
int* ptr;
{
    int x = 42;
    ptr = &x;       // x's scope ends here
}
// x's lifetime has ended — ptr is now dangling
*ptr = 99;          // UB: accessing object outside its lifetime
```

## Construction and Destruction of Local Variables

Local variables are destroyed in **reverse declaration order** when execution leaves their scope. This mirrors LIFO stack semantics.

```cpp
struct R {
    const char* name;
    R(const char* n) : name(n) { printf("ctor %s\n", name); }
    ~R()                        { printf("dtor %s\n", name); }
};

void f() {
    R a("a");   // constructed first
    R b("b");   // constructed second
    R c("c");   // constructed third
}
// output:
// ctor a
// ctor b
// ctor c
// dtor c  <-- reversed
// dtor b
// dtor a
```

## Early Exit Paths (return, throw, break)

Destruction still happens in reverse order on *any* exit path — this is the cornerstone of RAII.

```cpp
void process(bool fail) {
    std::lock_guard<std::mutex> lk(mtx);  // locks mutex
    std::vector<int> buf(1024);

    if (fail) return;   // lk destroyed here -> mutex unlocked automatically

    // ... more work ...
}   // lk destroyed here if not early-returned
```

Without RAII you would need to manually release resources on every exit path — error-prone in the presence of exceptions.

## Nested Scopes

Variables declared in an inner block are destroyed before variables in the outer block.

```cpp
void outer() {
    R x("outer");
    {
        R y("inner-1");
        R z("inner-2");
    }   // z, then y destroyed here
    // x destroyed here
}
```

## Lifetime Extension via const Reference

Binding a temporary to a `const` reference (or `auto&&`) extends the temporary's lifetime to match the reference's lifetime.

```cpp
const std::string& ref = std::string("hello");
// "hello" temporary lives as long as ref
```

This rule does *not* propagate through function parameters — only direct binding extends lifetime.

## Destruction Order of Globals and Statics

- **Global objects** are destroyed in reverse construction order after `main` returns.
- **Local statics** are destroyed in reverse order of their first initialization.
- Objects across different translation units: destruction order mirrors construction order (but construction order itself is unspecified across TUs — see the static initialization order fiasco).

```cpp
struct Tracker { ~Tracker() { puts("destroyed"); } };

Tracker t1;           // static duration
Tracker t2;           // static duration, constructed after t1

int main() {}
// output after main:
// destroyed  (t2, reverse order)
// destroyed  (t1)
```

## Common Pitfalls

**Accessing a destroyed object:**
```cpp
std::string* bad_ptr;
{
    std::string s = "alive";
    bad_ptr = &s;
}
// s is destroyed; bad_ptr is dangling
puts(bad_ptr->c_str());  // UB
```

**Relying on destruction order across TUs:** Don't. Use the function-static pattern to ensure safe initialization and destruction.

> **Interview answer:** Local objects are destroyed in reverse declaration order when they go out of scope, on all exit paths including exceptions and early returns. Globals are destroyed in reverse construction order after `main` returns. Lifetime and scope are distinct; a pointer to a local variable becomes dangling once the variable's lifetime ends.
