# volatile: What It Means in Embedded and OS Code

`volatile` is a qualifier that tells the compiler: "do not optimize away or reorder accesses to this variable — its value may change outside the normal program flow."

## The Problem volatile Solves

Compilers perform many optimizations: caching register values, hoisting loads out of loops, eliminating "redundant" reads. For ordinary variables these optimizations are safe. For hardware registers, shared ISR flags, and signal handlers, they silently produce wrong behavior.

```cpp
// WRONG: without volatile, compiler may read STATUS once and cache it
uint32_t* STATUS = (uint32_t*)0x4001'0000;
while (*STATUS & 0x01) { /* wait */ }  // infinite loop if optimizer removes repeated load

// CORRECT: volatile forces every iteration to re-read from the address
volatile uint32_t* STATUS = (volatile uint32_t*)0x4001'0000;
while (*STATUS & 0x01) { /* wait */ }
```

## Exactly What volatile Guarantees

- **Every read from a `volatile` object re-issues a load from memory** (or the mapped address).
- **Every write to a `volatile` object re-issues a store.**
- **Accesses are not eliminated**, even if the optimizer believes the value is unchanged.
- **Accesses to the same `volatile` object are not reordered** relative to each other by the compiler.

What `volatile` does **not** guarantee:
- No protection against CPU out-of-order execution (you still need memory barriers for that).
- No atomicity — a 64-bit volatile read may be split into two 32-bit bus transactions on a 32-bit bus.
- No synchronization between threads (use `std::atomic` for that).

## Memory-Mapped I/O

The most common use in embedded and OS code is **memory-mapped I/O (MMIO)**:

```cpp
// Cortex-M UART example
struct UART_Regs {
    volatile uint32_t DR;    // data register
    volatile uint32_t SR;    // status register
    volatile uint32_t CR;    // control register
};

UART_Regs* const UART0 = reinterpret_cast<UART_Regs*>(0x4000'C000);

void uart_send(uint8_t byte) {
    while (!(UART0->SR & 0x80)) {}  // wait for TX ready bit — must re-read SR each iteration
    UART0->DR = byte;
}
```

Without `volatile`, the optimizer may read `SR` once before the loop and never again, causing deadlock.

## ISR-Shared Flags

```cpp
volatile bool data_ready = false;   // set by ISR, polled by main loop

void uart_isr() {
    buffer[idx++] = UART0->DR;
    if (idx == FRAME_SIZE) data_ready = true;
}

void main_loop() {
    while (!data_ready) { /* spin */ }  // compiler must re-check data_ready each iteration
    process(buffer);
    data_ready = false;
}
```

Without `volatile`, the compiler may optimize `while (!data_ready)` into an infinite busy loop because it sees `data_ready` is never written in `main_loop`'s control flow.

## volatile and Signal Handlers (POSIX)

POSIX requires that variables shared between a signal handler and the main program be declared `volatile sig_atomic_t`:

```cpp
#include <signal.h>
volatile sig_atomic_t running = 1;

void handle_sigint(int) { running = 0; }

int main() {
    signal(SIGINT, handle_sigint);
    while (running) { /* work */ }
}
```

## Common Pitfalls

- **Using `volatile` for thread safety.** It prevents compiler caching but not CPU reordering. Use `std::atomic` instead.
- **Forgetting to cast the pointer.** `(uint32_t*)0x4000'0000` is not volatile. You must write `(volatile uint32_t*)0x4000'0000`.
- **Volatile struct members vs volatile struct.** A `volatile` struct makes all members volatile. A struct with `volatile` members is more explicit and preferred in MMIO peripheral models.
- **Performance cost.** Every access goes to memory. Keep volatile variables out of tight inner loops unless truly necessary.

> **Interview answer:** "`volatile` prevents the compiler from caching, eliminating, or reordering accesses to a variable. It is essential for hardware registers, ISR-shared flags, and signal handler variables, but it provides no atomicity or CPU memory-ordering guarantees."
