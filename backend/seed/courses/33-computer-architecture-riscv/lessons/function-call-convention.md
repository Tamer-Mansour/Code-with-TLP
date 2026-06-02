# The RISC-V Function Call Convention

The RISC-V calling convention is a complete protocol governing how one function invokes another: where arguments go, how return values come back, who saves which registers, and how the stack is managed. Mastering this protocol is essential for writing interoperable assembly, debugging C programs at the instruction level, and answering systems-programming interview questions.

## Overview of the Protocol

A function call involves four choreographed steps:

1. **Caller prepares arguments** — places values in `a0`–`a7` (and on the stack for extras).
2. **Caller transfers control** — `jal ra, target` or `call target` (pseudo).
3. **Callee executes** — using the frame it builds on entry.
4. **Callee returns** — places result in `a0`/`a1`, restores callee-saved registers, executes `ret`.

## Argument Passing Rules

| Argument | Location |
|----------|----------|
| 1st–8th integer/pointer | a0–a7 (x10–x17) |
| 9th and beyond | Stack, 8-byte aligned, pushed in order |
| 64-bit value in RV32 | Two consecutive registers (even-odd pair, e.g., a0:a1) |
| Struct ≤ 2 × XLEN | Two registers |
| Struct > 2 × XLEN | Caller allocates on stack; pointer passed in register |

## Return Value Rules

| Return type | Location |
|-------------|----------|
| Integer / pointer ≤ XLEN | a0 |
| Integer 2×XLEN (e.g. 64-bit on RV32) | a0:a1 (low:high) |
| Struct ≤ 2×XLEN | a0:a1 |
| Struct > 2×XLEN | Caller allocates buffer; address passed in a0 on entry |

## The Complete Call Sequence

```asm
# --- Caller side ---
# 1. Prepare arguments
li    a0, 10          # first argument
li    a1, 20          # second argument

# 2. Save any caller-saved registers still needed after the call
sw    t0, -4(sp)      # save t0 if it's live

# 3. Call
call  add_two         # jal ra, add_two

# 4. Use return value
mv    s0, a0          # result is in a0

# --- Callee side (add_two) ---
add_two:
    # Prologue: allocate frame
    addi  sp, sp, -16
    sw    ra, 12(sp)   # save ra (we call no one, but good habit)
    sw    s0,  8(sp)   # save s0 if used

    # Body
    add   a0, a0, a1   # a0 = a + b

    # Epilogue: restore and return
    lw    s0,  8(sp)
    lw    ra, 12(sp)
    addi  sp, sp, 16
    ret                # jalr x0, ra, 0
```

## Leaf vs Non-Leaf Functions

A **leaf function** makes no outgoing calls:

- It does not need to save `ra` (no call overwrites it).
- It may skip the stack frame entirely if it only uses caller-saved registers.

```asm
# Leaf: no frame needed
square:
    mul   a0, a0, a0   # a0 = a0 * a0
    ret                # ra unchanged, no stack manipulation needed
```

A **non-leaf function** calls other functions:

- Must save `ra` before the inner call.
- Must manage a complete prologue/epilogue.

## Variadic Functions

Variadic functions (like `printf`) follow a modified convention:
- Named arguments go in `a0`–`a7` as normal.
- Unnamed (variadic) arguments fill the remaining `a` registers, then spill to the stack.
- The callee accesses variadic args via a `va_list` which tracks the current position in registers and on the stack.

## Tail Calls

A tail call optimisation (TCO) replaces a call+return with a jump when the result of the called function is returned directly:

```asm
# Instead of: call foo; ret
# Use: j foo   (or jalr x0, ...)
# No new frame, no ra update needed
tail  foo      # pseudo: jal x0, foo
```

This keeps the call stack flat for recursive algorithms that qualify.

## System Calls

Linux on RISC-V uses a slight variation:
- `a7` holds the **syscall number**.
- `a0`–`a5` hold up to six arguments.
- Return value is in `a0` (negative values signal errors).
- Triggered by `ecall`.

```asm
li    a7, 64       # write syscall
li    a0, 1        # fd = stdout
la    a1, msg      # buffer address
li    a2, 13       # length
ecall
```

## Common Pitfalls

- **Not saving `ra` before a nested call.** The most frequent bug in hand-written assembly.
- **Passing the wrong number of registers.** Forgetting that a 64-bit value takes two registers on RV32.
- **Misaligning the stack.** Must be 16-byte aligned when `call` is executed.
- **Returning a value in the wrong register.** Return values go in `a0`, not `t0`.

> **Interview answer:** The RISC-V calling convention passes the first eight integer arguments in `a0`–`a7`, returns results in `a0`/`a1`, uses `jal ra, target` to call and `ret` to return, requires the stack to be 16-byte aligned at call boundaries, and mandates that callee-saved registers (`sp`, `s0`–`s11`) be restored before returning.
