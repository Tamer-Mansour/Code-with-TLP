# How the Optimizer Exploits UB

The C++ optimizer does not "do something wrong" when it eliminates your safety checks. It follows the rules of the standard precisely. Understanding this relationship — UB as a license for the optimizer — is essential for writing reliable systems code.

## The Fundamental Contract

The compiler is allowed to assume: **no execution of a well-formed program ever exhibits undefined behavior.**

Given this axiom, any code path that would only be reached through UB can be treated as *dead code* and eliminated. Any branch that would only be taken if UB occurred can be assumed to never execute.

## Example 1: Null Check Elimination

```cpp
int* global_ptr;

void init(int* p) {
    *p = 42;           // if p is null → UB (null deref)
    if (p == nullptr) {
        // The compiler proves: if we reached *p = 42 without UB,
        // p cannot be null. Therefore this branch is dead.
        handle_null();  // ELIMINATED
    }
}
```

A programmer might add the null check after the dereference "just in case." The compiler removes it. Compiling with `-O2` and inspecting the assembly confirms the check disappears.

## Example 2: Infinite Loop Elimination

```cpp
int count_to(int n) {
    int i = 0;
    while (i < n) {
        ++i;           // if i reaches INT_MAX and increments → UB
    }
    return i;
}
```

Because the loop increment overflows if run long enough (UB), and the standard says UB never happens, the compiler may conclude the loop always terminates quickly and hoist or reorder code around it.

## Example 3: Signed Overflow Comparison Folded to True

```cpp
bool will_overflow(int x) {
    return (x + 1) <= x;   // programmer's overflow detector
}
```

Compiled output at `-O2`:

```asm
; GCC/Clang output:
xor eax, eax    ; return false — always
ret
```

The expression `(x + 1) <= x` is mathematically false for non-overflowing integers, and since overflow is UB, the compiler proves it is always false.

## Example 4: Out-of-Bounds Eliminates Surrounding Logic

```cpp
int table[8];
int lookup(int i) {
    if (i >= 8) return -1;      // bounds guard
    return table[i];
}
```

If elsewhere the optimizer can prove `i` is always in `[0, 7]` when this function is called (perhaps by inlining), the bounds check is dead code and is removed — correctly. But if you *incorrectly* prove the bounds, the check disappears and the overflow is silent.

## The Optimizer Is Not Malicious

It helps to think of the optimizer as a mathematician working in the domain of programs-without-UB. It is doing everything right. The danger is when your mental model of the program includes UB-triggering paths that you consider "harmless" — the optimizer's model excludes those paths entirely.

## Viewing the Optimizer's Work

Use Compiler Explorer (godbolt.org) to inspect assembly:

```bash
# Local equivalent: compile to assembly
g++ -O2 -S -o prog.s prog.cpp
```

Compare the `-O0` and `-O2` outputs for functions containing potential UB. Disappearing branches are a strong signal.

## Defense Strategy

| Goal | Technique |
|---|---|
| Detect UB in dev/test | `-fsanitize=undefined,address` |
| Prevent null-check removal | Validate before dereferencing |
| Prevent overflow-check removal | Check before the operation |
| Understand what the optimizer sees | Compiler Explorer, `-S` flag |
| Suppress specific optimizations | `-fno-strict-overflow`, `-fwrapv` (with caveats) |

## Key Takeaway

> **Interview answer:** The optimizer assumes the program never exhibits UB, so any code that would only execute on a UB path is dead code and gets eliminated. This is how null checks after a dereference, post-increment overflow checks, and infinite loop protections disappear silently. The fix is to write UB-free code and validate with sanitizers — not to fight the optimizer.
