# SystemC Data Types: sc_int, sc_uint, sc_bv

SystemC provides a rich set of hardware-aware data types that go far beyond plain C++ integers. These types give you exact bit-width control, hardware operators, and modeling fidelity that `int` and `uint32_t` simply cannot provide.

## The Three Major Families

| Type family | Signed? | Arithmetic? | Typical use |
|-------------|---------|-------------|-------------|
| `sc_int<N>` | Yes | Yes | Signed registers, accumulators |
| `sc_uint<N>` | No | Yes | Addresses, counters, unsigned data paths |
| `sc_bv<N>` | N/A | No | Pure bit vectors, bus modeling |
| `sc_lv<N>` | N/A | No | Four-valued logic (0, 1, X, Z) |
| `sc_bigint<N>` | Yes | Yes | Wide signed (> 64 bits) |
| `sc_biguint<N>` | No | Yes | Wide unsigned (> 64 bits) |

`N` is a compile-time constant for `sc_int`/`sc_uint` (1–64) and can be larger for `sc_bigint`/`sc_biguint`.

## sc_int and sc_uint

These behave like hardware registers of exactly `N` bits, including overflow wrapping:

```cpp
sc_uint<4> nibble = 15;   // 0b1111
nibble++;                  // wraps to 0, just like a 4-bit counter
std::cout << nibble;       // prints 0

sc_int<8> s = -1;         // stored as 0xFF in two's complement
sc_int<8> t = 127;
sc_int<8> u = s + t;      // 0xFF + 0x7F = 0x7E = 126 (wraps in 8 bits)
```

### Bit-Select and Part-Select

```cpp
sc_uint<16> word = 0xABCD;

bool     bit3   = word[3];              // single bit
sc_uint<4> hi   = word.range(15, 12);  // bits 15 down to 12 → 0xA
sc_uint<8> lo   = word.range(7, 0);    // bits 7 down to 0  → 0xCD

// Write a range
word.range(3, 0) = 0xF;               // set lower nibble
```

Range indices follow the Verilog/VHDL convention: `range(high, low)`.

## sc_bv — Bit Vector

`sc_bv<N>` models a bus with no arithmetic semantics. It supports logical operations and string initialization:

```cpp
sc_bv<8> a = "10110101";   // binary string
sc_bv<8> b = 0x3C;

sc_bv<8> result = a & b;   // bitwise AND
sc_bv<8> shifted = a << 2; // left shift

// Convert to integer for arithmetic
int val = a.to_uint();
```

Use `sc_bv` when the signal represents a generic bus whose contents have varying interpretations depending on protocol state.

## sc_lv — Four-Valued Logic

`sc_lv<N>` extends `sc_bv` with `X` (unknown) and `Z` (high-impedance) states:

```cpp
sc_lv<4> bus = "01XZ";
std::cout << bus[0];   // '0'
std::cout << bus[2];   // 'X'
std::cout << bus[3];   // 'Z'
```

`sc_lv` is essential for modeling tri-state buses and uninitialized register detection.

## Type Conversions and Concatenation

```cpp
sc_uint<4> hi_nibble = 0xA;
sc_uint<4> lo_nibble = 0x5;

// Concatenation using comma operator in sc_bv context
sc_uint<8> byte_val;
byte_val.range(7, 4) = hi_nibble;
byte_val.range(3, 0) = lo_nibble;
// byte_val == 0xA5

// Or using the concatenation helper
sc_bv<8> bv_result = (sc_bv<4>(hi_nibble), sc_bv<4>(lo_nibble));
```

## Choosing the Right Type

```
Need arithmetic?  ──Yes──→  Signed? ──Yes──→  sc_int<N>  (N ≤ 64)
                  │                  ──No───→  sc_uint<N> (N ≤ 64)
                  │
                  ──No───→  Need X/Z? ──Yes──→  sc_lv<N>
                                      ──No───→  sc_bv<N>
```

For widths > 64 bits, use `sc_bigint<N>` or `sc_biguint<N>`.

## Common Pitfalls

- **Mixing `sc_uint<N>` with plain `int` in expressions** — implicit conversions can truncate silently; cast explicitly.
- **`range(low, high)` instead of `range(high, low)`** — the arguments are `(MSB, LSB)`, not `(LSB, MSB)`. Getting them backwards causes wrong values with no compiler warning.
- **Using `sc_bv` where arithmetic is needed** — `sc_bv` does not support `+` or `*`; use `sc_uint` and convert.
- **`sc_lv` in synthesizable code** — `X` and `Z` states are simulation-only; synthesis tools may reject or misinterpret them.

> **Interview answer:** "`sc_int<N>` and `sc_uint<N>` are N-bit hardware integer types with full arithmetic and bit-select operators. `sc_bv<N>` is a pure bit vector with no arithmetic, and `sc_lv<N>` adds four-valued logic (`0`, `1`, `X`, `Z`) for modeling unknowns and high-impedance. The correct choice depends on whether you need arithmetic and whether X/Z states are relevant."
