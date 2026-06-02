# Half Adders and Full Adders

Addition is the most fundamental operation in a CPU. Before building a 32-bit adder, every computer architect starts with the simplest possible building block: the **half adder**, then extends it to the **full adder**.

## The Half Adder

A half adder takes two single-bit inputs (A and B) and produces two single-bit outputs: a **Sum** bit and a **Carry** bit.

| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   |

The Boolean expressions are:

```
Sum   = A XOR B
Carry = A AND B
```

The half adder is called "half" because it cannot accept a carry-in from a previous bit position. That makes it only useful for the **least-significant bit** of a multi-bit addition.

## The Full Adder

A full adder adds two bits **plus a carry-in** (Cin), producing a Sum and a Carry-out (Cout). This is the building block that can be chained across all bit positions.

| A | B | Cin | Sum | Cout |
|---|---|-----|-----|------|
| 0 | 0 |  0  |  0  |  0   |
| 0 | 0 |  1  |  1  |  0   |
| 0 | 1 |  0  |  1  |  0   |
| 0 | 1 |  1  |  0  |  1   |
| 1 | 0 |  0  |  1  |  0   |
| 1 | 0 |  1  |  0  |  1   |
| 1 | 1 |  0  |  0  |  1   |
| 1 | 1 |  1  |  1  |  1   |

Boolean expressions:

```
Sum  = A XOR B XOR Cin
Cout = (A AND B) OR (Cin AND (A XOR B))
```

The second term `Cin AND (A XOR B)` captures the case where a carry is generated because exactly one of A or B is 1 and Cin pushes the total to 2.

## Building a Full Adder from Two Half Adders

A full adder can be constructed from two half adders and one OR gate:

```
Half Adder 1:  S1 = A XOR B,   C1 = A AND B
Half Adder 2:  Sum = S1 XOR Cin, C2 = S1 AND Cin
Cout = C1 OR C2
```

This is a useful identity: a full adder = two half adders + one OR gate.

## Chaining into a Ripple-Carry Adder

To add two N-bit numbers, chain N full adders. The carry-out of bit position *i* feeds the carry-in of bit position *i+1*. The very first carry-in is tied to 0 for addition (or 1 for subtraction, as we will see later).

```
Bit 0: FA(A[0], B[0], Cin=0)  → Sum[0], Cout[0]
Bit 1: FA(A[1], B[1], Cin=Cout[0]) → Sum[1], Cout[1]
...
Bit 31: FA(A[31], B[31], Cin=Cout[30]) → Sum[31], Cout[31]
```

The final carry-out (Cout[31]) becomes the **carry flag** of the ALU.

## Software Simulation

Understanding the logic is easier with a quick Python model:

```python
def half_adder(a, b):
    return a ^ b, a & b          # (sum, carry)

def full_adder(a, b, cin):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, cin)
    cout = c1 | c2
    return s2, cout

def ripple_carry_add(a_bits, b_bits):
    """a_bits, b_bits: lists of bits, LSB first"""
    result, carry = [], 0
    for a, b in zip(a_bits, b_bits):
        s, carry = full_adder(a, b, carry)
        result.append(s)
    return result, carry          # (sum bits LSB-first, final carry)
```

## Common Pitfalls

- **Half adder limitation**: forgetting it has no carry-in means it can only be used at position 0.
- **Carry propagation delay**: in a ripple-carry adder, bit 31 cannot complete until carries propagate through all 32 stages — this is the critical timing path.
- **Cout vs Overflow**: the final carry-out signals unsigned overflow; signed overflow requires comparing the carry into and out of the sign bit.

> **Interview answer:** A full adder adds three input bits (A, B, carry-in) producing a Sum and a Carry-out; chaining 32 full adders with the carry-out of each feeding the carry-in of the next produces a 32-bit ripple-carry adder.
