# Caller-Saved vs Callee-Saved Registers

When a function calls another function, both parties need to know whose responsibility it is to preserve each register's value across the call boundary. RISC-V's ABI divides the 32 registers into two camps: **caller-saved** and **callee-saved**.

## The Core Distinction

| Category | Also called | Who saves it | When is it safe to use freely? |
|----------|-------------|--------------|--------------------------------|
| Caller-saved | Volatile / temporary | The calling function | Before making a call |
| Callee-saved | Non-volatile / preserved | The called function | After the call returns |

Think of it as a hotel analogy: caller-saved registers are like a hotel lobby (the guest can rearrange the furniture, and the guest leaving must restore it themselves); callee-saved registers are like the hotel room itself (the guest checks out and everything must be back as found).

## RISC-V Caller-Saved Registers

These may be **freely overwritten by a callee** — the caller must save them before a call if their values are needed afterward.

| Registers | ABI names | Typical use |
|-----------|-----------|-------------|
| x1 | ra | Return address |
| x5–x7 | t0–t2 | Temporaries |
| x10–x17 | a0–a7 | Arguments / return values |
| x28–x31 | t3–t6 | Temporaries |

`ra` (x1) is caller-saved because the callee uses `ret` (which reads `ra`) and any nested call will overwrite `ra` with a new return address.

## RISC-V Callee-Saved Registers

These must be **preserved by the callee** — if a function uses them, it must save the old value (usually on the stack) and restore it before returning.

| Registers | ABI names | Typical use |
|-----------|-----------|-------------|
| x2 | sp | Stack pointer |
| x8–x9 | s0–s1 | Saved registers (s0 doubles as fp) |
| x18–x27 | s2–s11 | Saved registers |

`sp` is the most critical: mismanaging the stack pointer corrupts every future function call.

## Why Have Two Categories?

Having two categories is an **optimisation**. If every register were callee-saved, every function would push and pop all 31 registers even if it only used two. If every register were caller-saved, every call site would need to save every live register even when the callee touches none.

The split lets compilers be precise:

- A **leaf function** (no outgoing calls) can use all caller-saved registers without touching the stack at all.
- A **non-leaf function** saves only the callee-saved registers it actually uses, plus `ra`.

## Worked Example

```c
int foo(int x) {
    return bar(x) + baz(x);
}
```

Compiled to RISC-V:

```asm
foo:
    addi  sp, sp, -16
    sw    ra,  12(sp)   # save ra: foo calls bar and baz
    sw    s0,   8(sp)   # save s0 (callee-saved): we will use it to hold x
    mv    s0, a0        # s0 = x  (s0 survives the call to bar)

    call  bar           # a0 = x (from s0 if needed), result in a0
    mv    s1, a0        # save bar's result in s1 (callee-saved)

    mv    a0, s0        # reload x for baz
    call  baz           # result in a0

    add   a0, s1, a0    # return bar(x) + baz(x)

    lw    s0,  8(sp)    # restore s0
    lw    ra,  12(sp)   # restore ra
    addi  sp, sp, 16
    ret
```

Key observations:
- `ra` is saved because `call bar` will overwrite it.
- `x` is moved to `s0` (callee-saved) so it survives the call to `bar`.
- `bar`'s return value is moved to `s1` before calling `baz`.
- Caller-saved temporaries (`t0`–`t6`) are not saved because they are not live across a call boundary.

## Common Pitfalls

- **Forgetting to save `ra` in non-leaf functions.** This is the most common assembly bug: `ret` jumps to a garbage address because `ra` was overwritten by an inner call.
- **Using `s` registers without saving them.** If you write to `s2` you must restore it or you break the caller's data.
- **Assuming the compiler handles this automatically.** In hand-written assembly, you are the compiler. Track liveness manually.
- **Conflating "callee-saved" with "callee can't use it."** The callee can use any register — it just must restore callee-saved ones to their entry values.

> **Interview answer:** Caller-saved registers (`ra`, `t0`–`t6`, `a0`–`a7`) may be freely clobbered by a called function; the caller must save them if their values are needed after the call. Callee-saved registers (`sp`, `s0`–`s11`) must be preserved by the called function, which saves and restores them if it uses them.
