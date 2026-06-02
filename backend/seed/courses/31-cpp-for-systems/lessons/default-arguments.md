# Default Arguments and Their Pitfalls

Default arguments let callers omit trailing parameters, using a compiler-supplied value instead. They reduce boilerplate and keep APIs backward-compatible as new options are added.

## Basic Syntax

Default values are specified in the **declaration** (not the definition, if they are separate):

```cpp
// Declaration (in header)
void connect(const char* host, int port = 80, bool tls = false);

// Definition (in .cpp) — no defaults repeated
void connect(const char* host, int port, bool tls) {
    printf("connecting to %s:%d tls=%d\n", host, port, tls);
}

// Call sites
connect("example.com");          // port=80,  tls=false
connect("example.com", 443);     // port=443, tls=false
connect("example.com", 443, true); // explicit everything
```

Rules:

- Defaults must appear on **trailing** parameters — you cannot have a default in the middle and a non-default to its right.
- You cannot skip a middle argument; you must provide all preceding arguments.

```cpp
void f(int a, int b = 2, int c = 3);

f(1);        // a=1, b=2, c=3
f(1, 10);    // a=1, b=10, c=3
f(1, 10, 30); // a=1, b=10, c=30
// f(1, , 30)  -- ERROR: cannot skip b
```

## Default Arguments vs. Overloads

Both achieve similar call-site convenience but have different trade-offs:

| Aspect | Default arguments | Overloads |
|---|---|---|
| Code duplication | None (one function body) | Each overload has its own body |
| Virtual functions | Cannot use defaults polymorphically | Overloads work as expected |
| Name mangling | Single mangled name | Separate mangled names |
| Readability | Shows intent of "optional" in declaration | Each overload self-contained |

Default arguments are preferred for **one function with optional trailing parameters**. Overloads are better when each variant has genuinely different logic.

## Pitfall 1: Defaults in Both Declaration and Definition

Providing a default in the definition when a declaration already exists is an error:

```cpp
// header
void f(int x = 10);

// .cpp
void f(int x = 10) { ... }  // ERROR: redefinition of default argument
```

Only one location should specify each default.

## Pitfall 2: Defaults Are Evaluated at the Call Site

The default expression is evaluated **each time the default is used**, in the scope of the declaration:

```cpp
int global_timeout = 100;
void fetch(int ms = global_timeout);  // uses global_timeout at call time

// If global_timeout changes before the call, the new value is used
global_timeout = 500;
fetch();  // ms = 500, not 100
```

This is occasionally useful but often surprising. Prefer `const` or `constexpr` values as defaults.

## Pitfall 3: Hiding Overloads

Adding a default argument to an existing function can silently hide an intended overload:

```cpp
void process(int x);
void process(int x, int y = 0);  // now process(5) is ambiguous!
```

The compiler will issue an ambiguity error when both are in scope. Audit your overload sets before adding defaults.

## Pitfall 4: Virtual Functions and Defaults

Default arguments are resolved **statically** (at compile time, based on the static type of the pointer/reference), not dynamically. This means a derived class override's different default is invisible when called through a base pointer:

```cpp
struct Base    { virtual void f(int x = 10) { printf("B %d\n", x); } };
struct Derived : Base { void f(int x = 99) override { printf("D %d\n", x); } };

Base* p = new Derived;
p->f();  // prints "D 10" — Derived's override runs, but Base's default (10) is used!
```

> This is a well-known trap. The rule of thumb: **never use default arguments in virtual functions**.

## Worked Example: Logger with Defaults

```cpp
#include <cstdio>
#include <ctime>

enum Level { DEBUG, INFO, WARN, ERROR };

void log_msg(const char* msg, Level lvl = INFO, bool timestamp = false) {
    if (timestamp) printf("[%ld] ", (long)time(nullptr));
    const char* tags[] = {"DEBUG","INFO","WARN","ERROR"};
    printf("[%s] %s\n", tags[lvl], msg);
}

int main() {
    log_msg("system ready");              // INFO, no timestamp
    log_msg("low memory", WARN);          // WARN, no timestamp
    log_msg("kernel panic", ERROR, false); // ERROR, explicit false
}
```

**Output:**
```
[INFO] system ready
[WARN] low memory
[ERROR] kernel panic
```

> **Interview answer:** Default arguments are specified in the declaration, must be trailing, and are evaluated at the call site each time. The critical pitfall is that they interact badly with virtual dispatch — the default is chosen by the static (compile-time) type, not the runtime type.
