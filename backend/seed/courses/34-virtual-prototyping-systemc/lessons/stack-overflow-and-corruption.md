# Stack Overflow and Corruption Bugs

The stack is one of the most exploit-prone regions of memory in a running program. Two distinct failure classes dominate: **stack overflow** (the stack pointer crosses outside its allocated region) and **stack corruption** (data within the stack is overwritten incorrectly). Both cause crashes or — worse — silent data corruption and security vulnerabilities.

## Stack Overflow

A stack overflow occurs when the stack pointer moves below the bottom of the allocated stack region. The most common causes are:

- **Unbounded recursion** — a function calls itself without a base case, consuming a new frame on every call until memory is exhausted.
- **Oversized local arrays** — `char buf[1024 * 1024];` on the stack allocates 1 MB in a single function, which may exceed the default stack size.
- **Deep call chains in interrupt handlers** — embedded systems often place interrupt handlers on the same stack as the main thread; nested interrupts can overflow it quickly.

### Detection Mechanisms

| Mechanism | How it works |
|-----------|-------------|
| Guard page | OS maps a no-access page just below the stack; SP crossing it triggers a segfault / `SIGSEGV` |
| Stack canary | Compiler inserts a random value ("canary") between the frame and the return address; checked on return |
| Stack painting | RTOS or startup code fills the stack with a known pattern (e.g., `0xDEADBEEF`); a HWM probe scans for the first unpainted word |
| Hardware MPU | Embedded MCUs use a Memory Protection Unit region to catch SP crossing the stack limit |

### Example: Detecting a Guard Page Fault

```c
// This will overflow the default stack on most platforms (~8 MB on Linux)
void infinite_recurse(void) {
    char waste[4096];           // consume 4 KB per frame
    (void)waste;
    infinite_recurse();         // unconditional recursion
}

int main(void) {
    infinite_recurse();         // terminates with SIGSEGV
    return 0;
}
```

## Stack Corruption (Buffer Overflow on the Stack)

Stack corruption happens when a write through an invalid pointer or an unchecked buffer operation overwrites data in the current or an adjacent frame. Classic targets are the **return address** and the **saved frame pointer**.

```c
// Vulnerable function — classic stack buffer overflow
void vulnerable(const char *input) {
    char buf[16];
    strcpy(buf, input);   // no bounds check; input may be > 16 bytes
    // If input is 24 bytes, 8 bytes overwrite the saved RBP and return address
}
```

If an attacker controls `input`, they can overwrite the return address with a chosen value — the basis of **return-oriented programming (ROP)** attacks.

### Mitigation Techniques

- **Stack canaries** (`-fstack-protector-strong`): A random value placed between locals and the return address. A mismatch on function return triggers immediate abort.
- **ASLR (Address Space Layout Randomization)**: Randomizes stack base address, making it harder to predict where to jump.
- **SafeStack** (Clang): Separates the "unsafe" stack (holding return addresses) from the "safe" stack (holding local variables).
- **Shadow stack** (Intel CET / ARM PAC): Hardware maintains a separate read-only copy of return addresses; any mismatch faults immediately.

## Corruption Without Overflow: Use-After-Return

A subtler corruption bug occurs when a pointer to a stack variable escapes the function:

```c
int *dangling_pointer(void) {
    int local = 42;
    return &local;   // WARNING: local is destroyed on return
}

int main(void) {
    int *p = dangling_pointer();
    // The stack frame is gone; *p is garbage or may be overwritten
    printf("%d\n", *p);   // undefined behavior
}
```

GCC and Clang warn about this (`-Wreturn-local-addr`), and AddressSanitizer catches it at runtime.

## Virtual Prototype Perspective

In a SystemC VP:

- The ISS must model the **stack limit** register (e.g., `PSPLIM`/`MSPLIM` on Cortex-M33) and generate a fault when SP crosses it, replicating the hardware MPU behavior.
- Stack painting during VP startup (writing a known pattern to the simulated stack region) allows the VP to report high-water-mark stack usage — a key metric for firmware teams sizing their RAM.
- When the VP detects a corrupt return address (e.g., SP jumping to an unmapped region), a good ISS prints the PC, SP, and the last N executed instructions before stopping, making firmware debugging much faster than on real hardware.

> **Interview answer:** Stack overflow occurs when the stack pointer crosses outside the allocated stack region, usually due to infinite recursion or oversized locals. Stack corruption is when data in the stack frame — especially the return address — is overwritten by an out-of-bounds write, enabling crashes or security exploits. Mitigations include guard pages, stack canaries, ASLR, and hardware shadow stacks.
