# Bit Manipulation Tricks for Interviews

Bit manipulation problems appear frequently in technical interviews because they test your understanding of how computers represent and process data at the hardware level. Mastering a small toolkit of idioms lets you solve these problems quickly and confidently.

## Essential Toolkit

### Test a specific bit

```c
bool is_set = (x >> i) & 1;     // 1 if bit i of x is 1, else 0
```

### Set a specific bit

```c
x |= (1 << i);                  // set bit i to 1
```

### Clear a specific bit

```c
x &= ~(1 << i);                 // clear bit i to 0
```

### Toggle a specific bit

```c
x ^= (1 << i);                  // flip bit i
```

### Extract a bit field [high:low]

```c
uint32_t field = (x >> low) & ((1 << (high - low + 1)) - 1);
```

## Power-of-Two Tricks

These exploit a key property: powers of two in binary have exactly one bit set.

| Check | Expression | Why it works |
|-------|------------|--------------|
| Is x a power of two? | `x != 0 && (x & (x-1)) == 0` | x-1 flips all trailing zeros and the lowest set bit |
| Round down to power of two | Use bit scan / `__builtin_clz` | |
| Modulo by power of two | `x & (p - 1)` where p = 2^k | Equivalent to `x % p` for unsigned x |

```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def mod_power_of_two(x, p):
    """p must be a power of two."""
    return x & (p - 1)

print(is_power_of_two(64))   # True
print(is_power_of_two(60))   # False
print(mod_power_of_two(13, 8))  # 5  (13 % 8 = 5)
```

## Isolate and Remove the Lowest Set Bit

```c
int lowest_bit  = x & (-x);     // isolate lowest set bit
int clear_lowest = x & (x - 1); // clear lowest set bit
```

The expression `x & (-x)` works because `-x` in two's complement flips all bits above the lowest 1 and preserves the lowest 1.

Counting set bits (Kernighan's algorithm):

```c
int count_bits(int x) {
    int count = 0;
    while (x) {
        x &= (x - 1);   // clears lowest set bit each iteration
        count++;
    }
    return count;
}
```

This runs in O(k) where k is the number of set bits — much faster than O(N) if k is small.

## XOR Identity Tricks

XOR has three useful identities:

- `a ^ a = 0` — any value XORed with itself is zero
- `a ^ 0 = a` — XOR with zero is identity
- XOR is commutative and associative

Classic interview use: find the single non-duplicate element in an array where every other element appears twice.

```python
def find_single(nums):
    result = 0
    for n in nums:
        result ^= n       # all pairs cancel out; single element remains
    return result

print(find_single([4, 1, 2, 1, 2]))  # 4
```

## Swap Without a Temp Variable

```c
a ^= b;
b ^= a;
a ^= b;
// After: a and b are swapped — but never use this in real code (UB if a==b alias)
```

This is a classic trick for interviews; in production, just use a temp variable.

## Sign and Magnitude Tricks

```c
// Absolute value without branching (for 32-bit signed int)
int mask = x >> 31;           // 0x00000000 if x >= 0, 0xFFFFFFFF if x < 0
int abs_x = (x + mask) ^ mask;

// Check if two integers have opposite signs
bool opp_signs = (a ^ b) < 0; // MSB = 1 means they differ in sign
```

## Bit Reversal

```python
def reverse_bits(n, width=32):
    result = 0
    for _ in range(width):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```

## Interview Cheat-Sheet

| Problem | One-liner trick |
|---------|----------------|
| Count set bits | `bin(x).count('1')` in Python; `__builtin_popcount(x)` in C |
| Check odd/even | `x & 1` (1=odd, 0=even) |
| Multiply by 2^k | `x << k` |
| Divide by 2^k (unsigned) | `x >> k` |
| Test if power of 2 | `x && !(x & (x-1))` |
| Get/clear lowest set bit | `x & -x` / `x & (x-1)` |
| Toggle sign | Arithmetic right shift trick above |
| Find non-duplicate | XOR all elements |

## Common Pitfalls

- **Signed shift**: `>>` on signed types is implementation-defined in C — use `uint32_t` for bit manipulation.
- **Shift amount >= word size**: `1 << 32` on a 32-bit int is undefined behavior in C. Use `1LL << 32` or mask the shift amount.
- **Two's complement assumption**: these tricks assume two's complement representation, which is guaranteed in C since C20 and in all modern hardware.
- **Priority of `&` vs `==`**: `x & mask == 0` is parsed as `x & (mask == 0)` in C — always parenthesize: `(x & mask) == 0`.

> **Interview answer:** The most important bit manipulation identities are `x & (x-1)` to clear the lowest set bit (used for power-of-two checks and popcount), `x & -x` to isolate the lowest set bit, and XOR self-cancellation (`a^a=0`) to find unique elements — all execute in constant time using native CPU instructions.
