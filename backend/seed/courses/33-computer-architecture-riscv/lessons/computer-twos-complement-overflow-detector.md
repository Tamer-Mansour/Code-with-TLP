# Two's Complement Overflow Detector

One of the most important distinctions between RISC-V and its predecessors like MIPS is that RISC-V's `ADD` instruction **never traps on signed overflow**. Instead of raising an exception, the result silently wraps around in 32-bit two's complement. Knowing when that wraparound has occurred — and whether the unsigned carry-out also fired — is the programmer's responsibility.

## Why RISC-V Has No Overflow Flag

RISC-V follows the RISC philosophy of keeping the ISA minimal. There is no status register with flags like x86's EFLAGS or ARM's CPSR. If you need overflow detection, you test for it explicitly in software after the addition.

## The Two Conditions to Detect

### Signed Overflow

Signed overflow in 32-bit addition occurs when two operands of the **same sign** produce a result with the **opposite sign**:

- Both inputs positive, result negative: positive + positive wrapped to a negative number.
- Both inputs negative, result positive (or zero): negative + negative wrapped around past the minimum.

The mathematical test is:

```
overflow = (A > 0 AND B > 0 AND result < 0)
        OR (A < 0 AND B < 0 AND result >= 0)
```

In RISC-V assembly, the classic idiom is:

```asm
add   t0, t1, t2        # compute A + B
xor   t3, t1, t2        # if inputs have different signs, overflow is impossible
bltz  t3, no_overflow   # bit 31 set → different signs, skip
xor   t4, t0, t1        # result sign vs input sign
bltz  t4, overflow      # bit 31 set → signs differ → overflow occurred
no_overflow:
```

### Unsigned Carry-Out

Unsigned carry-out occurs when the true mathematical sum of the two operands (treated as unsigned 32-bit values) exceeds 2^32 − 1. The hardware discards the 33rd bit; detecting it requires comparing the 32-bit truncated result against one of the operands:

```asm
add   t0, t1, t2
# If carry occurred, t0 < t1 (unsigned), because adding wrapped around
bltu  t0, t1, carry_occurred
```

## The Four Possible Combinations

| Signed Overflow | Unsigned Carry | Example (32-bit)             |
|-----------------|---------------|------------------------------|
| NO              | NO            | 100 + 200 = 300              |
| NO              | YES           | 0xFFFFFFFF + 1 = 0 (wraps)   |
| YES             | NO            | 2000000000 + 2000000000      |
| YES             | YES           | -1 + -1 = -2 (signed fine but unsigned wraps) |

## RISC-V vs MIPS Comparison

MIPS provided two addition instructions: `ADD` (traps on signed overflow) and `ADDU` (no trap). RISC-V eliminates the trapping version entirely and provides only the non-trapping `ADD`. This simplifies the hardware and pipeline, but shifts the correctness burden to software and compilers.

## Practical Detection in C

For safe checked addition in C, use compiler builtins rather than trying to detect after the fact:

```c
#include <stdbool.h>
#include <stdint.h>

bool safe_add(int32_t a, int32_t b, int32_t *result) {
    return __builtin_add_overflow(a, b, result);
}
```

Alternatively, widen to 64-bit, perform the addition, then check:

```c
int64_t wide = (int64_t)a + (int64_t)b;
bool overflow = (wide > INT32_MAX) || (wide < INT32_MIN);
*result = (int32_t)wide;
```

## Key Takeaways

- RISC-V `ADD` wraps silently — no flag, no trap.
- Signed overflow and unsigned carry-out are **independent** conditions.
- Overflow: same-sign inputs, opposite-sign result.
- Carry: unsigned sum exceeds 2^32.
- Use compiler builtins or widen-and-check idioms for safe arithmetic in C.

## Further Reading

- *Computer Organization and Design RISC-V Edition* by Patterson and Hennessy — Chapter 3: Arithmetic for Computers covers overflow detection hardware in detail.
- The RISC-V Unprivileged Specification (https://docs.riscv.org/reference/isa/_attachments/riscv-unprivileged.pdf) — Section 2.4 on integer computational instructions.
