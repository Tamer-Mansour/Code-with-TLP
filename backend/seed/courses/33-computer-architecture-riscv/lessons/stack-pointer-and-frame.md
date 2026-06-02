# The Stack Pointer and Stack Frames

The **stack** is a contiguous region of memory used to store temporary data that does not fit in registers: saved register values, local variables, and function call metadata. The **stack pointer** (`sp`, x2) tracks the current top of this region. Understanding stack frames is essential for reading and writing correct assembly, debugging crash dumps, and passing technical interviews.

## Stack Direction and the Stack Pointer

On RISC-V (and most modern architectures), the stack **grows downward**: high addresses are older frames, low addresses are newer ones. `sp` always points to the **lowest valid byte** currently in use — the "top" of the stack in the logical sense.

```
High address   ┌──────────────┐
               │  main's frame │
               ├──────────────┤  ← sp on entry to main
               │  foo's frame  │
               ├──────────────┤  ← sp on entry to foo
               │  bar's frame  │
               ├──────────────┤  ← sp on entry to bar
Low address    │   (free)      │
```

## Allocating and Deallocating a Frame

A function creates a stack frame by **subtracting** from `sp` at entry and restoring it at exit:

```asm
# Entry: allocate 32-byte frame
addi  sp, sp, -32

# Exit: deallocate frame
addi  sp, sp, 32
ret
```

The ABI requires `sp` to be **16-byte aligned** at every function call boundary. Frames are therefore always a multiple of 16 bytes.

## Stack Frame Layout

A typical stack frame contains, from low address to high:

```
sp+0   │ local variable 1  │
sp+4   │ local variable 2  │
sp+8   │ saved s0          │
sp+12  │ saved ra          │
       └───────────────────┘  ← previous sp (caller's sp)
```

Compilers vary the exact layout, but saved `ra` is almost always at a fixed offset from `sp` so that debuggers and profilers can unwind the call stack.

## The Frame Pointer (s0 / fp)

The frame pointer is an **optional** stable reference into the current frame. When enabled:

- `fp` = `sp` + frame_size (i.e., the value `sp` had at function entry).
- Local variables and saved registers are addressed as `fp - offset` (fixed regardless of further `sp` movement).

```asm
addi  sp, sp, -32
sw    fp, 28(sp)    # save old fp
sw    ra, 24(sp)    # save return address
addi  fp, sp, 32    # fp = caller's sp
```

Frame pointers simplify debugging and stack unwinding but are omitted by optimizing compilers (`-fomit-frame-pointer`) to free up `s0` as a general-purpose saved register.

## Worked Example: Local Variables on the Stack

```c
int sum(int n) {
    int total = 0;      // local variable
    for (int i = 1; i <= n; i++) total += i;
    return total;
}
```

```asm
sum:
    addi  sp, sp, -16
    sw    s0, 12(sp)    # save s0 (will hold 'total')
    sw    s1,  8(sp)    # save s1 (will hold 'i')
    li    s0, 0         # total = 0
    li    s1, 1         # i = 1
loop:
    bgt   s1, a0, done  # if i > n, exit
    add   s0, s0, s1    # total += i
    addi  s1, s1, 1     # i++
    j     loop
done:
    mv    a0, s0        # return total
    lw    s1,  8(sp)
    lw    s0, 12(sp)
    addi  sp, sp, 16
    ret
```

Note that `total` and `i` live in callee-saved registers rather than on the stack — the compiler prefers registers when the function is a leaf (no outgoing calls). The stack is used here only to preserve the caller's `s0` and `s1`.

## Stack Overflow

If a program recurses too deeply or allocates too many local variables, `sp` drops below the lowest valid stack page and a **page fault** (stack overflow) occurs. The OS provides a guard page just below the stack to catch this. Common causes:

- Unbounded recursion.
- Large stack-allocated arrays (prefer heap allocation for large buffers).
- Interrupt or signal handlers that reuse the user stack without adequate headroom.

## Common Pitfalls

- **Misaligning `sp`.** Allocating 12 bytes instead of 16 breaks alignment and can cause faults on systems with strict alignment checking.
- **Forgetting to restore `sp`.** If `sp` is off by even 4 bytes on return, the caller's frame is corrupt.
- **Accessing stack memory after deallocation.** Once `sp` moves up, that memory may be reused by an interrupt handler or the next function call at any time.

> **Interview answer:** `sp` (x2) points to the lowest in-use stack byte; the stack grows downward. A function allocates its frame by subtracting from `sp` on entry, stores saved registers and local data in the frame, and restores `sp` before returning. The ABI requires 16-byte alignment of `sp` at every call boundary.
