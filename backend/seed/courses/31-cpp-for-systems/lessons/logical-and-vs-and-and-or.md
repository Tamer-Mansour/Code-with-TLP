# & vs && and | vs ||: Bitwise vs Logical Operators

One of the most common sources of bugs in systems code is accidentally using a bitwise operator where a logical one was intended, or vice versa. The symbols look similar but the semantics are completely different.

## The Two Families at a Glance

| Operator | Family | Operand types | Result type | Short-circuits? |
|----------|--------|--------------|-------------|----------------|
| `&` | Bitwise AND | integers | integer | No |
| `\|` | Bitwise OR | integers | integer | No |
| `^` | Bitwise XOR | integers | integer | No |
| `~` | Bitwise NOT | integer | integer | N/A |
| `&&` | Logical AND | any scalar | `bool` | Yes |
| `\|\|` | Logical OR | any scalar | `bool` | Yes |
| `!` | Logical NOT | any scalar | `bool` | N/A |

## Bitwise Operators: Working on Individual Bits

Bitwise operators treat integers as arrays of bits and apply the operation bit-by-bit.

```cpp
uint8_t a = 0b1010'1100;  // 0xAC = 172
uint8_t b = 0b1111'0000;  // 0xF0 = 240

uint8_t and_result = a & b;   // 0b1010'0000 = 0xA0 = 160
uint8_t or_result  = a | b;   // 0b1111'1100 = 0xFC = 252
uint8_t xor_result = a ^ b;   // 0b0101'1100 = 0x5C = 92
uint8_t not_result = ~a;      // 0b0101'0011 = 0x53 = 83
```

### Essential Bit Manipulation Patterns

```cpp
uint32_t flags = 0;

// Set bit N
flags |= (1u << N);

// Clear bit N
flags &= ~(1u << N);

// Toggle bit N
flags ^= (1u << N);

// Test if bit N is set
bool is_set = (flags >> N) & 1u;
// or:
bool is_set2 = (flags & (1u << N)) != 0;
```

Note: always use `1u` (unsigned) when building masks. Using `1` (signed `int`) and shifting it into the sign bit is undefined behavior.

## Logical Operators: Boolean Truth

Logical operators treat any non-zero value as `true` and zero as `false`. They always return `bool`.

```cpp
int x = 5, y = 0;

bool land = x && y;   // false (5 is truthy, 0 is falsy → false)
bool lor  = x || y;   // true  (5 is truthy → true, y not evaluated)
bool lnot = !x;       // false (5 is truthy → !true = false)
```

## The Critical Bug: Confusing & and &&

```cpp
int errno_val = get_error();
int flags     = get_flags();

// WRONG — always evaluates both sides, treats errno_val as a mask
if (errno_val & flags) { /* ... */ }

// CORRECT — if errno_val is zero (no error), short-circuits
if (errno_val && flags) { /* ... */ }
```

A more dangerous case:

```cpp
char* ptr = get_pointer();

// WRONG: & does not short-circuit — *ptr is evaluated even when ptr is null!
if (ptr & *ptr == 'A') { /* crash if ptr is null */ }

// CORRECT: && short-circuits — *ptr only evaluated when ptr is non-null
if (ptr && *ptr == 'A') { /* safe */ }
```

## The Reverse Error: && Instead of &

```cpp
uint8_t status = read_status_register();

// WRONG: logical AND — any non-zero status is "true", bitwise mask lost
if (status && 0x04) {  // always true when status != 0, regardless of bit 2
    handle_ready();
}

// CORRECT: bitwise AND — test exactly bit 2
if (status & 0x04) {
    handle_ready();
}
```

## Bitwise NOT vs Logical NOT

```cpp
uint8_t mask = 0b11110000;
uint8_t inverted = ~mask;   // 0b00001111 — flips all bits

int x = 5;
bool negated = !x;          // false — logical negation
int weird    = !mask;       // 0 (mask is non-zero → true → !true = 0)
```

`~0` is the all-ones pattern for any integer width and is commonly used to create full bitmasks.

## Compound Bitwise Assignment

All bitwise operators have compound assignment forms:

```cpp
uint32_t reg = 0xDEAD'0000;
reg |= 0x0000'BEEF;   // set lower half: 0xDEADBEEF
reg &= 0xFFFF'0000;   // clear lower half: 0xDEAD0000
reg ^= 0xFFFF'FFFF;   // flip all bits: 0x2152FFFF
reg <<= 4;            // shift left 4: logical shift
reg >>= 2;            // shift right 2: logical if unsigned
```

**Interview answer:** "Bitwise operators (&, |, ^, ~) operate on individual bits of integers. Logical operators (&&, ||, !) coerce operands to bool and short-circuit. Confusing them is a common bug: & with a null-pointer guard allows the dereference to execute; && with a bitmask check loses the bit pattern."
