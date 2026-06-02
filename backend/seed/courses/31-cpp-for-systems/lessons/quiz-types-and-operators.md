# Quiz: Fundamental Types, Variables, and Operators

Test your understanding of C++ fundamental types, integer behavior, floating-point representation, and operator semantics.

---

**Q1. On a 64-bit Linux system using the LP64 data model, what is `sizeof(long)`?**

- [ ] 4
- [x] 8
- [ ] 16
- [ ] Platform-dependent, cannot be determined

LP64 (Linux/macOS 64-bit) defines `long` as 64 bits (8 bytes). On Windows 64-bit (LLP64), `long` is only 32 bits — this is the most common portability trap when moving code between platforms.

---

**Q2. What does the following code print?**

```cpp
#include <cstdio>
int main() {
    int  s = -1;
    unsigned int u = 1;
    printf("%s\n", s < u ? "less" : "not less");
}
```

- [ ] `less`
- [x] `not less`
- [ ] Undefined behavior — no output
- [ ] Compilation error

When a signed and unsigned int of the same rank are compared, the signed value is converted to unsigned. `-1` becomes `UINT_MAX` (4294967295), which is NOT less than 1. Enable `-Wsign-compare` to catch this at compile time.

---

**Q3. Which of the following is the correct way to test whether bit 3 (zero-indexed) of `status` is set?**

```cpp
uint8_t status = 0b0001'1010;
```

- [ ] `if (status && (1 << 3))`
- [ ] `if (status & 8 == 1)`
- [x] `if ((status & (1u << 3)) != 0)`
- [ ] `if (status | (1u << 3))`

Option A uses `&&` (logical, not bitwise). Option B has a precedence bug: `==` binds tighter than `&`, so it reads as `status & (8 == 1)` = `status & 0` = 0. Option D tests if either bit is set, not if bit 3 is set. Option C is correct: bitwise AND with the mask, then explicit comparison to zero.

---

**Q4. What is the value of `result` after this code executes?**

```cpp
uint8_t a = 200, b = 100;
uint8_t result = a + b;
```

- [ ] 300
- [x] 44
- [ ] Undefined behavior
- [ ] 255 (saturates)

`a` and `b` are promoted to `int` before addition: `int(200) + int(100) = 300`. The result `300` is then narrowed back to `uint8_t`: `300 % 256 = 44`. There is no saturation in standard C++ integer arithmetic.

---

**Q5. Which statement about `NaN` in IEEE 754 is correct?**

- [ ] `NaN == NaN` evaluates to `true`
- [ ] `NaN` is greater than any finite number
- [x] `NaN != NaN` evaluates to `true`; use `std::isnan()` to detect it
- [ ] `NaN` is only produced by division by zero

NaN is the only value in IEEE 754 that is not equal to itself — `NaN != NaN` is `true`. Division by zero with floats produces `Inf`, not `NaN`. `NaN` is produced by `0.0/0.0`, `sqrt(-1)`, and similar indeterminate operations. Always use `std::isnan()` to test for it.

---

**Q6. What is the result of the following expression, and why?**

```cpp
int x = 1 + 2 << 3;
```

- [ ] 17 — shift applied first: `1 + 16`
- [ ] 1 — addition and shift cancel
- [x] 24 — addition applied first: `(1+2) << 3 = 3 * 8`
- [ ] Undefined behavior — mixing addition and shift

Addition (`+`) has higher precedence than left shift (`<<`), so the expression groups as `(1 + 2) << 3 = 3 << 3 = 24`. This is a common source of bugs in code that mixes arithmetic and bitwise shifts — always use parentheses to make intent explicit.
