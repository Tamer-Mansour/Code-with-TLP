# Choosing Value vs Pointer vs Reference

Picking the right parameter-passing style is a design decision, not a style preference. The wrong choice can silently copy megabytes of data, hide mutation from callers, or introduce crashes from null dereferences. This lesson consolidates the rules into a repeatable decision process.

## The Decision Tree

```
Is the argument optional (may be absent / null)?
  YES → use pointer (T* or const T*)
  NO  ↓
Does the function need to modify the caller's object?
  YES → use non-const reference (T&)
  NO  ↓
Is the type cheap to copy (scalar, pointer, small POD ≤ 2 words)?
  YES → pass by value (T)
  NO  → use const reference (const T&)
```

Follow this tree top-to-bottom and you will be correct in the vast majority of cases.

## Quick-Reference Table

| Condition | Style | Example |
|---|---|---|
| Optional / nullable | `T*` | `void log(FILE* f)` |
| Must modify, always present | `T&` | `void fill(Buffer& buf)` |
| Read-only, large object | `const T&` | `void print(const Matrix& m)` |
| Cheap type, read-only | `T` (value) | `void sq(int n)` |
| Sink / consume (move) | `T` (value) | `Widget(std::string name)` |
| C-API interop | `T*` | `memcpy(void* dst, ...)` |

## Scalar Types: Always by Value

For `bool`, `char`, `int`, `float`, `double`, and pointers themselves, pass by value. Passing `const int&` adds a hidden pointer indirection and never helps:

```cpp
// Bad — unnecessary indirection
void bad(const int& n) { std::cout << n * 2; }

// Good — one register, zero overhead
void good(int n) { std::cout << n * 2; }
```

## Large Objects: const Reference by Default

```cpp
// Bad — copies an entire vector on every call
void process(std::vector<double> data);

// Good — zero copy, compiler-enforced immutability
void process(const std::vector<double>& data);
```

A rough rule: if `sizeof(T) > 2 * sizeof(void*)` (i.e., larger than two pointers), strongly prefer `const T&` over `T`.

## Sink Parameters: Value + Move

When a constructor or function is going to *own* the argument, take it by value and move it in. This way, an lvalue is copied once and an rvalue is moved (zero copies):

```cpp
class Server {
    std::string host_;
public:
    explicit Server(std::string host)   // by value
        : host_(std::move(host)) {}     // move into member
};

// Caller passes lvalue → one copy, one move
// Caller passes rvalue → zero copies, one move
```

## Output Parameters: Reference or Pointer?

Both work. The dominant guidance in modern C++ style guides:

- **Prefer returning a value** (with RVO, it is often free).
- **Use a non-const reference** when multiple outputs are needed without a struct.
- **Use a pointer** when the output is optional.

```cpp
// Option 1: return value (best when one output)
std::string toUpper(const std::string& s);

// Option 2: non-const reference (multiple outputs)
void parseLine(const std::string& line, int& id, std::string& name);

// Option 3: pointer (optional output)
bool tryParse(const std::string& s, int* outVal);
```

## Worked Example: Mixed Styles in One Function

```cpp
#include <vector>
#include <string>

// src: read-only large object → const ref
// out: output buffer → non-const ref
// maxLen: cheap scalar → value
// logFile: optional → pointer
void extract(const std::vector<char>& src,
             std::string& out,
             int maxLen,
             FILE* logFile) {
    out.assign(src.begin(),
               src.begin() + std::min((int)src.size(), maxLen));
    if (logFile) {
        std::fprintf(logFile, "extracted %zu bytes\n", out.size());
    }
}
```

Every parameter style here is justified by the decision tree.

## Common Pitfalls

- Using `const T&` for `int` or `double` — adds indirection, gains nothing.
- Forgetting that `T` by value copies the whole object — surprising with `std::string`.
- Returning `T&` to a local variable — dangling reference.
- Not null-checking pointer parameters — undefined behavior on null dereference.

> **Interview answer:** Use `const T&` for large read-only objects, `T&` for mandatory output parameters, `T*` for optional/nullable arguments, and plain `T` for cheap scalars or sink parameters. When in doubt, prefer returning a value over output parameters.
