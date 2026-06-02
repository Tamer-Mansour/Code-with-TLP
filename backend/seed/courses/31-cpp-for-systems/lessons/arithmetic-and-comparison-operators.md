# Arithmetic, Comparison, and Assignment Operators

These operators are the bread and butter of every C++ program. They look simple, but each one has edge cases that matter in low-level code.

## Arithmetic Operators

| Operator | Name | Notes |
|----------|------|-------|
| `+` | Addition | Signed overflow = UB |
| `-` | Subtraction | Unary `-` also exists |
| `*` | Multiplication | Result may need wider type |
| `/` | Division | Integer division truncates toward zero |
| `%` | Modulo (remainder) | Result sign matches dividend in C++11+ |

### Integer Division and Modulo

```cpp
int a = 7, b = -3;
int q = a / b;   // -2  (truncation toward zero, C++11+)
int r = a % b;   //  1  (7 = (-2)*(-3) + 1)

// Verify: q * b + r == a  always holds
printf("%d\n", q * b + r);  // 7
```

Before C++11 the direction of truncation for negative division was implementation-defined. C++11 mandates truncation toward zero.

Division by zero is **undefined behavior** for integers and produces `Inf` or `NaN` for floats.

### Multiplication Overflow

```cpp
int32_t a = 100000, b = 100000;
int32_t product = a * b;  // 10,000,000,000 overflows int32_t — UB!

// Fix: promote before multiplying
int64_t safe = (int64_t)a * b;  // 10000000000 — correct
```

The cast must happen *before* the multiplication, not after.

## Comparison Operators

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

All comparison operators return `bool` (`true` or `false`, which are integer 1 and 0).

The classic pitfall: comparing signed and unsigned types silently promotes the signed value.

```cpp
int size = get_size();     // may return -1 on error
if (size < sizeof(buffer)) // sizeof returns size_t (unsigned)!
    fill(buffer, size);    // executes even when size == -1!
```

## Assignment Operators

C++ provides compound assignment for every arithmetic and bitwise operator:

```cpp
int x = 10;
x += 5;   // x = x + 5  → 15
x -= 3;   // x = x - 3  → 12
x *= 2;   // x = x * 2  → 24
x /= 4;   // x = x / 4  → 6
x %= 4;   // x = x % 4  → 2
```

Assignment returns a reference to the left-hand operand, enabling chaining:

```cpp
int a, b, c;
a = b = c = 0;  // right-to-left: c=0, then b=0, then a=0
```

### Increment and Decrement

```cpp
int i = 5;
int pre  = ++i;  // i becomes 6, pre = 6
int post = i++;  // post = 6, then i becomes 7
```

- **Pre-increment** returns the incremented value (no copy needed for non-trivial types).
- **Post-increment** must return the *old* value, so it creates a copy internally.

In tight loops on complex iterator types, prefer `++it` over `it++`.

## The Comma Operator

The comma operator evaluates both operands left-to-right and returns the rightmost value. It is rarely needed and often confusing:

```cpp
int x = (1 + 2, 3 + 4);  // x = 7 (left side discarded)
```

The only idiomatic use is in `for` loop headers:

```cpp
for (int i = 0, j = 10; i < j; ++i, --j) { /* ... */ }
```

## Worked Example: Safe Absolute Value

```cpp
#include <climits>

// abs(INT_MIN) is UB — there is no positive INT_MIN in two's complement
int safe_abs(int x) {
    if (x == INT_MIN) return INT_MAX;  // closest we can get
    return x < 0 ? -x : x;
}
```

`std::abs` from `<cstdlib>` has this same UB for `INT_MIN` — handle it explicitly in security-sensitive code.

**Interview answer:** "Integer division in C++11+ truncates toward zero. Multiplying two 32-bit values can overflow — cast one operand to 64-bit before the multiplication. Post-increment returns a copy of the old value, so prefer pre-increment for iterator types to avoid unnecessary copies."
