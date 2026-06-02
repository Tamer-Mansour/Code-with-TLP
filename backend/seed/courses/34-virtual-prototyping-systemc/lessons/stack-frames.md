# Stack Frames and Function Prologue/Epilogue

Every function call carves out a private region of the stack called a **stack frame** (also called an **activation record**). This frame holds all the data the function needs during its lifetime: saved registers, local variables, and sometimes spilled arguments. The code that creates a frame is the **prologue**; the code that tears it down is the **epilogue**.

## Anatomy of a Stack Frame

A typical x86-64 frame (System V ABI) looks like this immediately after the prologue:

```
Higher address (caller's frame)
┌──────────────────────────────┐
│  arg 7, arg 8, ...           │ ← passed on stack if > 6 args
│  return address              │ ← pushed by CALL
│  saved RBP (frame pointer)   │ ← pushed by prologue
├──────────────────────────────┤ ← RBP points here (optional)
│  local variable 1            │
│  local variable 2            │
│  saved callee-saved regs     │
│  red zone (128 bytes, leaf)  │
└──────────────────────────────┘ ← RSP points here
Lower address (current frame top)
```

## The Frame Pointer (FP / RBP)

The **frame pointer** is an optional second register (x86-64: `RBP`, ARM: `R11` or `FP`, AArch64: `X29`) that points to a fixed location within the current frame. Its purpose is to provide a stable base address throughout the function even as SP moves (e.g., when calling sub-functions or using `alloca`).

Modern compilers often omit the frame pointer (`-fomit-frame-pointer`) to free the register for general use, relying on DWARF `.eh_frame` / `.debug_frame` tables for unwinding instead.

## Function Prologue

The prologue runs at the very start of a function:

```asm
; x86-64 prologue (with frame pointer)
push   rbp          ; save caller's frame pointer
mov    rbp, rsp     ; set our frame pointer = current SP
sub    rsp, 32      ; allocate 32 bytes for locals + alignment
push   rbx          ; save callee-saved register
push   r12          ; save callee-saved register
```

Equivalent C-level view:

```c
int add(int a, int b) {
    // prologue: save RBP, set RBP=RSP, allocate frame
    int result = a + b;   // local variable lives in the frame
    return result;
    // epilogue: restore RSP from RBP (or add), restore RBP, ret
}
```

## Function Epilogue

The epilogue reverses the prologue:

```asm
; x86-64 epilogue (with frame pointer)
pop    r12          ; restore callee-saved register
pop    rbx          ; restore callee-saved register
mov    rsp, rbp     ; collapse local allocation (SP = FP)
pop    rbp          ; restore caller's frame pointer
ret                 ; pop return address → RIP
```

On x86-64 the `LEAVE` instruction is a shorthand for `MOV RSP, RBP` + `POP RBP`.

## ARM Cortex-M Example

```asm
; ARM Thumb-2 prologue
PUSH  {R4, R5, R6, LR}  ; save regs + link register
SUB   SP, SP, #16        ; allocate 16 bytes of locals

; ... body ...

; ARM Thumb-2 epilogue
ADD   SP, SP, #16        ; deallocate locals
POP   {R4, R5, R6, PC}  ; restore regs; popping into PC = return
```

Popping directly into `PC` is an ARM idiom that performs the return in the same instruction as the register restore.

## Stack Frame Chaining

Each saved frame pointer forms a **linked list** of frames:

```
RBP → [saved RBP of caller] → [saved RBP of caller's caller] → ... → 0
```

Debuggers and profilers walk this chain to produce a **stack trace** (backtrace). An ISS-based profiler in a virtual prototype can reconstruct the same chain by reading the FP register and following saved-FP values in simulated memory.

## Common Pitfalls

- **Forgetting to align SP.** The prologue must ensure 16-byte alignment before any `CALL` inside the body. If the prologue pushes an odd number of 8-byte registers, it must add an extra 8-byte pad.
- **Variable-length arrays (VLAs).** A VLA causes SP to move by a runtime-determined amount, invalidating the simple "SP offset = local variable address" model. Compilers must use the frame pointer when VLAs are present.
- **Leaf function optimization.** Leaf functions (those that call no other function) can skip saving LR/RA and skip allocating a full frame, using the "red zone" below SP (128 bytes on x86-64) for temporaries. An ISS must respect this: a signal or interrupt that fires during a leaf function must not clobber the red zone.

> **Interview answer:** A stack frame is the portion of the stack allocated by one function call. The prologue saves the caller's frame pointer and return address, allocates space for locals, and saves callee-saved registers. The epilogue restores those registers, deallocates locals, and executes RET to pop the return address back into the instruction pointer.
