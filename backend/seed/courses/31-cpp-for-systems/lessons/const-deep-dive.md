# const: Variables, Pointers, and Methods Revisited

The `const` qualifier is one of C++'s most powerful correctness tools. It tells the compiler — and your teammates — that something must not change. Understanding its placement rules is essential for writing robust systems code.

## const Variables

A `const` variable must be initialized at declaration and cannot be modified afterward.

```cpp
const int MAX_RETRIES = 5;   // OK
// MAX_RETRIES = 6;          // compile error
```

In C++, `const` at namespace or file scope has **internal linkage** by default (unlike C), so you can safely put it in headers without violating the One Definition Rule.

## Pointer and const: Three Combinations

This is where most developers stumble. Read declarations **right to left**:

| Declaration | Pointer mutable? | Pointee mutable? |
|---|---|---|
| `int* p` | yes | yes |
| `const int* p` | yes | no |
| `int* const p` | no | yes |
| `const int* const p` | no | no |

```cpp
int x = 10, y = 20;

const int* p1 = &x;   // pointer to const int
// *p1 = 99;          // ERROR — can't change x through p1
p1 = &y;              // OK — p1 itself can be redirected

int* const p2 = &x;   // const pointer to int
*p2 = 99;             // OK — x is now 99
// p2 = &y;           // ERROR — p2 is fixed

const int* const p3 = &x;  // read-only all the way
```

**Rule of thumb:** `const` applies to what is immediately to its left. If nothing is to its left, it applies to what is immediately to its right.

## const in Function Parameters

Passing by `const` reference is the idiomatic way to accept large objects without copying and without allowing modification:

```cpp
void print_config(const Config& cfg) {
    // cfg.name is readable but cfg.name = "new" would be a compile error
}
```

Passing a raw pointer to `const` is the C-compatible equivalent, common in OS and embedded code:

```cpp
ssize_t write(int fd, const void* buf, size_t count);
```

The `const void*` signals: "I will read from your buffer but never write to it."

## const Member Functions

A `const` member function guarantees it will not modify the object's observable state:

```cpp
class Register {
    uint32_t value_;
public:
    uint32_t read() const { return value_; }  // safe to call on const objects
    void write(uint32_t v) { value_ = v; }    // non-const — modifies state
};

const Register status_reg = get_status();
status_reg.read();   // OK
// status_reg.write(1); // ERROR
```

Only `const` member functions can be called on `const` objects or through `const` references.

## Common Pitfall: const and Casts

`const_cast` removes constness at runtime. In systems code, **never** use it unless you are interfacing with a legacy C API that takes `char*` but provably never writes through the pointer.

```cpp
legacy_c_func(const_cast<char*>(str.c_str()));  // justified only if API is read-only
```

Writing through a casted-away `const` pointer is **undefined behavior**.

## Practical Worked Example

```cpp
// Typical driver pattern: read-only configuration struct
struct PinConfig {
    uint8_t pin_number;
    bool    active_high;
};

void configure_gpio(const PinConfig& cfg) {
    // compiler ensures we cannot accidentally write cfg.pin_number = 0
    uint8_t reg = cfg.active_high ? 0x01 : 0x00;
    write_hw_register(cfg.pin_number, reg);
}
```

> **Interview answer:** "`const` on a variable means it cannot be modified after initialization. On a pointer, it can bind to the pointer, the pointee, or both. On a method, it means the method cannot modify the object's state and can be called on `const` instances."
