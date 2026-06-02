# The Stack Pointer Register

The **stack pointer (SP)** is a dedicated CPU register that always holds the address of the current "top" of the stack. Because the stack grows downward, "top" actually means the lowest currently-used address. Every push, pop, function call, and function return is ultimately implemented as an arithmetic operation on SP followed by a memory access.

## Architecture Names for SP

Different ISAs name the register differently, but the concept is identical:

| Architecture | SP register | Width |
|---|---|---|
| x86-32 | `ESP` | 32 bits |
| x86-64 | `RSP` | 64 bits |
| ARM (A32/T32) | `R13` / `SP` | 32 bits |
| AArch64 | `SP` (or `X31` in some contexts) | 64 bits |
| RISC-V | `x2` (ABI name `sp`) | 32 or 64 bits |
| MIPS | `$29` (ABI name `$sp`) | 32 or 64 bits |

## How SP Is Initialized

In a bare-metal embedded system the startup code (often called `_start` or `Reset_Handler`) sets SP before jumping to `main`:

```asm
; ARM Cortex-M example (vector table entry)
; The first 32-bit word of the vector table is the initial SP value.
; The processor loads it automatically on reset — no code needed.

; RISC-V bare-metal startup
_start:
    la   sp, _stack_top    # load address of top-of-stack symbol
    jal  ra, main
```

In Linux user-space the kernel sets up the initial `RSP` (x86-64) before `_start` is entered. The C runtime then aligns it to 16 bytes before calling `main`.

## SP Alignment Rules

The ABI mandates that SP must be aligned to a specific boundary **at the point of a function call**:

- **x86-64 System V ABI**: SP must be 16-byte aligned *before* the `CALL` instruction executes (which pushes the return address, making it 8-byte aligned inside the callee's prologue).
- **AArch64 ABI**: SP must always be 16-byte aligned.
- **ARM AAPCS32**: SP must be 4-byte aligned at all times; 8-byte alignment is required at public interfaces.

Violating alignment causes SIMD loads/stores to fault (`#GP` on x86) or silently corrupt data on some microarchitectures.

## Reading and Writing SP in Code

In most high-level C code you never touch SP directly. But you can read it for diagnostics:

```c
#include <stdint.h>

static uintptr_t read_sp(void) {
    uintptr_t sp;
#if defined(__x86_64__)
    __asm__ volatile ("mov %%rsp, %0" : "=r"(sp));
#elif defined(__aarch64__)
    __asm__ volatile ("mov %0, sp" : "=r"(sp));
#elif defined(__riscv)
    __asm__ volatile ("mv %0, sp" : "=r"(sp));
#endif
    return sp;
}
```

This pattern is useful in firmware diagnostics and stack-usage profilers.

## SP in a Virtual Prototype ISS

Inside a SystemC ISS, the register file is typically modeled as an array or struct. Every decoded instruction that modifies SP triggers an update to that struct. The ISS must also check for stack overflow — when SP drops below the bottom of the mapped stack region:

```cpp
// Conceptual ISS check after a stack-decrement instruction
void iss_check_stack(uint64_t new_sp) {
    if (new_sp < STACK_BASE) {
        SC_REPORT_ERROR("ISS", "Stack overflow detected");
        sc_stop();
    }
}
```

> **Interview answer:** The stack pointer is a dedicated register that holds the address of the current stack top. Because the stack grows downward, a push decrements SP first and then writes; a pop reads first and then increments SP. The ABI defines the required alignment of SP at call boundaries (16 bytes on x86-64 and AArch64) and violation leads to faults or data corruption.
