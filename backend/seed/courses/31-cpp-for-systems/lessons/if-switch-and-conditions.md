# if, switch, and Conditional Expressions

Branching is the foundation of every control-flow decision a program makes. C++ gives you three primary tools: `if`/`else if`/`else`, `switch`, and the ternary conditional operator. Knowing when each is appropriate — and what can go wrong — is essential for writing fast, readable systems code.

## The if / else Chain

```cpp
int classify(int x) {
    if (x < 0)       return -1;
    else if (x == 0) return  0;
    else             return  1;
}
```

Key points:

- The condition must be a scalar or pointer type; any non-zero value is `true`.
- Braces are optional for single-statement bodies, but omitting them is a common source of bugs.
- The compiler evaluates branches top-to-bottom and takes the **first** true branch.

### Pitfall: assignment inside condition

```cpp
if (n = 0)   // assigns 0, condition is always false — bug!
if (n == 0)  // comparison — what you meant
```

Some style guides mandate `(0 == n)` (Yoda conditions) to make accidental assignment a compile error.

## switch

`switch` is best when a single integral value is compared against a known set of constants:

```cpp
void handle(int opcode) {
    switch (opcode) {
        case 0x01: write_reg(); break;
        case 0x02: read_mem();  break;
        case 0xFF: shutdown();  break;
        default:   unknown_op(opcode); break;
    }
}
```

Rules and pitfalls:

| Feature | Detail |
|---|---|
| Case labels | Must be integer constant expressions |
| Fall-through | Execution continues to the next case unless `break` (or `return`) is present |
| `default` | Optional but recommended as a safety net |
| Variable declarations | Jumping over a declaration with an initializer is ill-formed |

**Intentional fall-through** should be annotated with `[[fallthrough]]` (C++17) to silence compiler warnings and document intent:

```cpp
case 'a':
case 'e':
    [[fallthrough]];   // both hit vowel handler
case 'i':
    handle_vowel(); break;
```

## The Ternary (Conditional) Operator

```cpp
int abs_val = (x < 0) ? -x : x;
```

Good for **short, single-expression** selections — especially initializing `const` variables. Avoid nesting ternaries; they become unreadable fast.

```cpp
// Readable
const char* label = (score >= 90) ? "A" : (score >= 80) ? "B" : "C";

// Prefer if/else once it needs more than one line of logic
```

## Compile-Time Branching: if constexpr

In template code, `if constexpr` discards the untaken branch at compile time, preventing instantiation errors:

```cpp
template<typename T>
void print_size() {
    if constexpr (sizeof(T) == 4)
        puts("32-bit type");
    else
        puts("other width");
}
```

## Worked Example: Parsing an Error Code

```cpp
#include <cstdio>

const char* decode_errno(int e) {
    switch (e) {
        case 0:    return "OK";
        case 1:    return "EPERM";
        case 2:    return "ENOENT";
        case 12:   return "ENOMEM";
        default:   return "UNKNOWN";
    }
}

int main() {
    int codes[] = {0, 2, 12, 99};
    for (int c : codes)
        printf("code %3d -> %s\n", c, decode_errno(c));
}
```

**Output:**
```
code   0 -> OK
code   2 -> ENOENT
code  12 -> ENOMEM
code  99 -> UNKNOWN
```

> **Interview answer:** Use `switch` when dispatching on a single integral value against a known constant set — the compiler can optimize it to a jump table. Use `if`/`else if` when conditions involve ranges, multiple variables, or non-integral types. Use the ternary operator for concise single-expression choices only.
