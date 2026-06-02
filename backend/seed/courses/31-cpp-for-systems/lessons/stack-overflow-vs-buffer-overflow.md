# Stack Overflow vs Stack Buffer Overflow

These two terms sound similar but describe completely different failure modes. Confusing them is a common interview mistake.

## Stack Overflow

A **stack overflow** occurs when the call stack runs out of space. Each function call pushes a new stack frame containing local variables, saved registers, and the return address. When the total stack depth exceeds the OS limit (typically 1–8 MB), the next frame write hits an unmapped guard page and the OS delivers SIGSEGV.

**Most common cause: unbounded recursion.**

```cpp
int factorial(int n) {
    return n * factorial(n - 1);   // no base case → infinite recursion
}

int main() {
    std::cout << factorial(100000) << "\n";   // stack overflow
}
```

Each call to `factorial` pushes a new frame. After tens of thousands of calls the stack is exhausted.

**Other causes:**
- Very large local arrays (e.g., `char buf[4000000];` on the stack)
- Deep mutual recursion that is not tail-call optimized

## Stack Buffer Overflow

A **stack buffer overflow** is a *bounds violation* within a single stack frame. A local buffer is written past its end into adjacent stack memory. The stack size is not exceeded; the *contents* of the stack are corrupted.

```cpp
void process(const char* input) {
    char buf[32];
    strcpy(buf, input);   // if input > 31 chars → stack buffer overflow
}
```

The call stack may be only one level deep, but the overflow can overwrite the saved return address of that single frame.

## Side-by-Side Comparison

| Aspect | Stack Overflow | Stack Buffer Overflow |
|---|---|---|
| Root cause | Too many nested calls | Write past end of local buffer |
| Stack usage | Exceeds total stack size | Corrupts *within* a frame |
| Immediate crash | Yes — guard page hit | Sometimes (depends on what is overwritten) |
| Security impact | DoS / crash | Code execution possible |
| Detection | OS signal / backtrace | ASan, stack canary |
| Fix | Add base case / increase stack / use heap | Bounds-checked writes, `std::string` |

## How to Diagnose Each

**Stack overflow in GDB:**
```
Program received signal SIGSEGV, Segmentation fault.
(gdb) bt
#0  factorial (n=99823) at fact.cpp:2
#1  factorial (n=99824) at fact.cpp:2
... (thousands of frames)
```

The backtrace shows the same function repeated thousands of times.

**Stack buffer overflow in GDB / ASan:**
```
==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffef4a0b040
WRITE of size 64 at 0x7ffef4a0b040 thread T0
    #0 0x401234 in process prog.cpp:3
```

A single frame, one write, past the end of `buf`.

## Increasing Stack Size (When Appropriate)

For deep-but-finite recursion on legitimate data:

```bash
# Linux: raise to 64 MB for the current shell
ulimit -s 65536
```

Or refactor to an iterative approach with an explicit stack on the heap:

```cpp
// Iterative factorial — no stack depth issue
long long factorial(int n) {
    long long result = 1;
    for (int i = 2; i <= n; ++i) result *= i;
    return result;
}
```

## Key Takeaway

> **Interview answer:** A stack overflow exhausts the total stack space (usually from infinite recursion), while a stack buffer overflow is a bounds violation inside a single frame that corrupts adjacent stack data. They trigger SIGSEGV in different ways and require different fixes.
