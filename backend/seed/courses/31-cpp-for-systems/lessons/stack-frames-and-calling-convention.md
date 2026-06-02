# Stack Frames and the Calling Convention

Every function call involves a precise protocol between caller and callee: who saves which registers, how arguments are passed, where the return value goes, and how the stack is cleaned up. This protocol is the *calling convention*.

## Anatomy of a Stack Frame (x86-64 System V ABI)

When `caller` calls `callee`, the stack looks like this just after the prologue:

```
High address
+---------------------------+
|  caller's locals          |
+---------------------------+
|  return address           |  <-- pushed by CALL instruction
+---------------------------+
|  saved RBP (old frame ptr)|  <-- pushed by callee prologue
+---------------------------+  <-- RBP points here
|  callee's locals          |
|  spilled registers        |
+---------------------------+  <-- RSP points here
Low address
```

The **frame pointer** (RBP) anchors the frame so debuggers and stack-unwinding code can walk the call chain even when RSP changes.

## The x86-64 System V Calling Convention (Linux, macOS)

### Integer/Pointer Arguments (first 6)
Passed in registers: `RDI, RSI, RDX, RCX, R8, R9`

### Floating-Point Arguments (first 8)
Passed in: `XMM0 – XMM7`

### Additional arguments
Pushed on the stack right-to-left.

### Return value
- Integer/pointer: `RAX` (and `RDX` for 128-bit)
- Float: `XMM0`

### Caller-saved vs callee-saved registers

| Caller-saved (volatile) | Callee-saved (non-volatile) |
|-------------------------|-----------------------------|
| RAX, RCX, RDX, RSI, RDI, R8–R11, XMM0–XMM15 | RBX, RBP, R12–R15 |

The callee *may* trash caller-saved registers; if the caller needs them after the call it must save them first. Callee-saved registers must be restored before returning.

## Example: Tracing a Simple Call

```cpp
int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(3, 4);
}
```

Approximate assembly (AT&T syntax):

```asm
main:
    mov  $3, %edi       ; first arg in RDI
    mov  $4, %esi       ; second arg in RSI
    call add
    ; RAX now holds 7
    ret

add:
    push %rbp           ; save old frame pointer
    mov  %rsp, %rbp     ; establish new frame pointer
    ; a is in EDI, b is in ESI
    lea  (%rdi,%rsi), %eax   ; eax = a + b
    pop  %rbp           ; restore frame pointer
    ret                 ; return, result in EAX
```

## Windows x64 Calling Convention (Differences)

- First 4 integer args: `RCX, RDX, R8, R9` (not 6).
- First 4 float args: `XMM0–XMM3`.
- **Shadow space:** caller must reserve 32 bytes above the return address even if fewer than 4 args are used.
- The callee may store register args in the shadow space for debugging.

## Why Calling Conventions Matter for Systems Programming

- **FFI / interoperability:** Calling a C library from C++, Rust, or Python via `ctypes` requires matching the exact convention.
- **Inline assembly / intrinsics:** You must respect register constraints to avoid corrupting the caller's state.
- **Stack unwinding:** Exception handling and profilers walk stack frames using the saved RBP chain or DWARF/CFI tables.
- **Tail-call optimization:** A call in tail position can reuse the current frame (same RSP), eliminating a push/pop pair — but only if the convention allows it.

```cpp
// Tail call: compiler can optimize to a JMP rather than CALL
int factorial(int n, int acc = 1) {
    if (n <= 1) return acc;
    return factorial(n - 1, n * acc);   // tail call
}
```

> **Interview answer:** A calling convention specifies which registers carry arguments and the return value, which registers must be preserved across calls, and how the stack is set up and torn down. On x86-64 Linux the first six integer arguments go in RDI/RSI/RDX/RCX/R8/R9 and the return value in RAX.
