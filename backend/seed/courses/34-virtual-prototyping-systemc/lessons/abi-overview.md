# What an ABI Specifies

A **calling convention** governs how one function calls another. An **ABI (Application Binary Interface)** is the broader contract that governs how separately compiled binary units — object files, shared libraries, the kernel, and the C runtime — interoperate at the machine-code level. The calling convention is one chapter of the ABI; the rest specifies everything else a binary needs to run correctly.

## ABI vs. API

| | API | ABI |
|---|---|---|
| Level | Source code | Machine code / binary |
| Contract about | Function signatures, types, macros | Register usage, data layout, object format |
| Broken by | Renaming a function | Changing struct layout, register assignment |
| Detected by | Compiler | Only at runtime (silently) |

An API break is caught at compile time. An ABI break compiles silently but causes crashes or data corruption at runtime — making it far more dangerous.

## What an ABI Specifies

### 1. Calling Convention

Covered in the previous lesson: which registers carry arguments, return values, and which must be saved by caller vs. callee.

### 2. Data Type Sizes and Alignment

The ABI fixes the width of every fundamental type. This is why `int` is 32 bits on both ILP32 and LP64 Linux/x86-64 — the ABI mandates it.

| Type | ILP32 (32-bit) | LP64 (64-bit Linux) | LLP64 (64-bit Windows) |
|------|---------------|---------------------|------------------------|
| `char` | 8 | 8 | 8 |
| `short` | 16 | 16 | 16 |
| `int` | 32 | 32 | 32 |
| `long` | 32 | **64** | **32** |
| `long long` | 64 | 64 | 64 |
| `pointer` | 32 | 64 | 64 |

The difference in `long` between LP64 and LLP64 is a common source of portability bugs.

### 3. Struct Layout and Padding

The ABI specifies how structures are laid out in memory, including padding bytes inserted for alignment. Two compilers targeting the same ABI must produce identical struct layouts so that one library can pass a struct pointer to another.

```c
// On x86-64 System V ABI:
struct Example {
    char  a;      // offset 0, size 1
    // 3 bytes padding
    int   b;      // offset 4, size 4
    char  c;      // offset 8, size 1
    // 7 bytes padding
    long  d;      // offset 16, size 8
};               // total size = 24 bytes
```

The `__attribute__((packed))` GCC extension removes ABI-mandated padding, creating non-ABI-compliant structs that cannot safely be shared across compilation units.

### 4. Object File Format and Symbol Mangling

- **ELF** (Executable and Linkable Format) on Linux/embedded
- **PE/COFF** on Windows
- **Mach-O** on macOS

C++ name mangling is also ABI-defined. The Itanium C++ ABI (used on Linux/macOS) mangles `void foo(int, double)` as `_Z3foodd`. MSVC uses a different mangling — a major source of incompatibility between GCC/Clang and MSVC on Windows.

### 5. System Call Interface

On Linux the system call ABI specifies:
- System call number in `RAX`
- Arguments in `RDI, RSI, RDX, R10, R8, R9`
- Return value in `RAX`
- Invocation via `SYSCALL` instruction

This is intentionally different from the function-call ABI (which uses `RCX` for arg 4, not `R10`) to avoid the `SYSCALL` instruction clobbering `RCX`.

### 6. Exception Handling and Stack Unwinding

The ABI includes tables (`.eh_frame` / `.debug_frame` in DWARF format) that describe how to unwind each stack frame without a frame pointer. These tables enable C++ exceptions and debugger backtraces to work even in optimized builds.

## ABI Stability and Versioning

System ABIs are extremely stable: Linux has kept its x86-64 syscall ABI unchanged since 2001. Breaking the ABI requires updating every shared library and every binary that depends on it — essentially a full OS reinstall. This is why distributing pre-compiled libraries is risky: a library compiled for glibc 2.17 will run on glibc 2.35, but not vice versa.

## Virtual Prototype Perspective

When bringing up a new SoC virtual prototype, the firmware team and the VP team must agree on the ABI:

- Which registers hold arguments to boot ROM functions
- How structs are laid out in shared memory between CPU cores
- What the system call numbers are in the embedded OS

An ABI mismatch between the ISS and the firmware compiler causes subtle failures: the ISS reads arguments from the wrong registers, struct fields appear to have garbage values, and exceptions unwind incorrectly. Reviewing the toolchain's ABI documentation (e.g., the ARM AAPCS or RISC-V psABI) before starting VP bring-up avoids these pitfalls.

> **Interview answer:** An ABI specifies the complete binary-level contract between software components: calling convention, data type sizes and alignment, struct layout and padding rules, object file format, symbol name mangling, system call interface, and stack-unwinding tables. Unlike an API break (caught at compile time), an ABI break compiles silently and causes runtime crashes or data corruption.
