# Calling Conventions: Args, Return Values, Saved Regs

A **calling convention** is the agreed-upon contract between a function caller and a function callee about how arguments are passed, how return values come back, and which registers each side is responsible for preserving. Without a shared convention, code compiled by different compilers — or written by hand — cannot call each other correctly.

## Why Calling Conventions Exist

Consider two separately compiled translation units. The caller pushes arguments in some order; the callee reads them from somewhere. If they disagree on where arguments live, the callee reads garbage. Calling conventions eliminate this ambiguity by standardizing:

1. Where arguments go (registers vs. stack, and in what order)
2. Where the return value goes
3. Which registers a callee may freely clobber ("caller-saved")
4. Which registers a callee must preserve ("callee-saved")
5. Who cleans up stack arguments (caller or callee)

## x86-64 System V ABI (Linux, macOS, most POSIX)

This is the dominant convention for 64-bit desktop and server software.

| Role | Registers |
|------|-----------|
| Integer/pointer args 1–6 | `RDI, RSI, RDX, RCX, R8, R9` |
| Floating-point args 1–8 | `XMM0–XMM7` |
| Return value (integer) | `RAX` (and `RDX` for 128-bit) |
| Return value (FP) | `XMM0` |
| Caller-saved (volatile) | `RAX, RCX, RDX, RSI, RDI, R8–R11, XMM0–XMM15` |
| Callee-saved (non-volatile) | `RBX, RBP, R12–R15` |

Arguments beyond the sixth are pushed right-to-left onto the stack. The **caller** cleans them up.

```c
// C declaration
long add3(long a, long b, long c);
// Assembly equivalent (caller side)
// mov rdi, a
// mov rsi, b
// mov rdx, c
// call add3
// result in rax
```

## Windows x64 ABI

Microsoft uses a different convention on 64-bit Windows:

| Role | Registers |
|------|-----------|
| Integer/pointer args 1–4 | `RCX, RDX, R8, R9` |
| FP args 1–4 | `XMM0–XMM3` |
| Return value (integer) | `RAX` |
| Caller-saved | `RAX, RCX, RDX, R8–R11, XMM0–XMM5` |
| Callee-saved | `RBX, RBP, RDI, RSI, R12–R15, XMM6–XMM15` |

Windows x64 also mandates a 32-byte **shadow space** (home space) allocated by the caller above the return address — even if fewer than four arguments are passed. This space can be used by the callee to spill its register arguments.

## ARM AAPCS32 (32-bit ARM)

| Role | Registers |
|------|-----------|
| Args 1–4 | `R0–R3` |
| Return value | `R0` (and `R1` for 64-bit results) |
| Caller-saved | `R0–R3, R12 (IP), LR` |
| Callee-saved | `R4–R11, SP` |
| Link register | `LR` (R14) holds return address |

## AArch64 (AAPCS64)

| Role | Registers |
|------|-----------|
| Integer/pointer args 1–8 | `X0–X7` |
| FP/SIMD args 1–8 | `V0–V7` |
| Return value | `X0` (integer), `V0` (FP) |
| Caller-saved | `X0–X17, V0–V31` |
| Callee-saved | `X18–X28, X29 (FP), X30 (LR), SP` |

## Caller-Saved vs. Callee-Saved

The distinction determines where the compiler inserts save/restore code:

```c
// Caller-saved example
void outer(void) {
    long x = expensive_computation();
    inner();        // inner() may clobber RDX (caller-saved)
    use(x);         // compiler must save x before call if x lives in RDX
}

// Callee-saved example
void inner(void) {
    // compiler saves R12 at entry, restores at exit
    // caller can rely on R12 being unchanged after inner() returns
}
```

## Stack Cleanup: cdecl vs. stdcall

On 32-bit x86 two common variants differ in who pops stack arguments:

- **cdecl** (C default): the **caller** adds `ESP` back. Supports variadic functions (`printf`).
- **stdcall** (Windows API): the **callee** pops with `RET N`. Slightly smaller call sites but no variadic support.

## Virtual Prototype Perspective

A VP's ISS must implement the calling convention to correctly simulate system calls, interrupt handlers, and firmware function calls. When a simulated interrupt fires, the ISS must save the caller-saved registers to the stack before dispatching the handler, exactly as hardware does. An ISS that skips this step runs firmware incorrectly — functions appear to return garbage values.

> **Interview answer:** A calling convention specifies which registers carry arguments and return values, which registers a callee must save and restore (callee-saved), and which registers a caller must save if it needs them after the call (caller-saved). x86-64 System V uses RDI/RSI/RDX/RCX/R8/R9 for the first six integer arguments and RAX for the return value.
