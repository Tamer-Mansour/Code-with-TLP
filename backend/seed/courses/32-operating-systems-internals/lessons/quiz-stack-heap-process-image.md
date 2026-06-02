# Quiz: Memory Layout: Stack, Heap, and the Process Image

Test your understanding of stack and heap mechanics, process image layout, alignment, and common memory errors.

---

**Q1. Which of the following best describes how stack memory is allocated when a function is called?**

- [ ] The OS allocates a new memory page for each function call.
- [ ] The allocator searches the free list for a suitable block.
- [x] The CPU decrements the stack pointer by the size of the new frame.
- [ ] A garbage collector reserves space on the stack at runtime.

*The stack pointer (RSP on x86-64) is decremented by the compiler-computed frame size — allocation is a single arithmetic instruction, making it O(1) and extremely fast.*

---

**Q2. A C program contains the following declaration at file scope: `int counters[10000];` (no initializer). In which memory segment does this variable live?**

- [ ] .data (initialized data segment)
- [x] .bss (block started by symbol)
- [ ] Heap
- [ ] Stack

*Uninitialized (or zero-initialized) global variables go to .bss. The OS zero-fills BSS pages lazily — no zeros are stored in the binary file, keeping executable size small.*

---

**Q3. Consider this struct on a 64-bit system:**
```c
struct S { char a; double b; char c; };
```
**What is the most likely value of `sizeof(struct S)`?**

- [ ] 10
- [ ] 11
- [ ] 16
- [x] 24

*`a` sits at offset 0 (1 byte). `b` (double, alignment 8) requires 7 bytes of padding, sitting at offset 8. `c` sits at offset 16. Trailing padding (7 bytes) rounds the total to a multiple of 8: 24.*

---

**Q4. What is a use-after-free bug?**

- [ ] Calling `free()` on a pointer that was never allocated with `malloc`.
- [ ] Allocating memory and never freeing it, causing a leak.
- [x] Accessing heap memory after it has already been freed.
- [ ] Using a stack variable after it has been moved to the heap.

*Use-after-free reads or writes memory that the allocator has returned to the free list. The region may have been re-allocated for other data, causing corruption or a security vulnerability.*

---

**Q5. Which tool would BEST help you find a memory leak in a C program at runtime?**

- [x] Valgrind with `--leak-check=full`
- [ ] `strace` (system call tracer)
- [ ] `gdb` with a hardware breakpoint
- [ ] `nm` (symbol table lister)

*Valgrind instruments every heap allocation and reports blocks that were allocated but not freed when the program exits, including the allocation call stack.*

---

**Q6. What happens when a recursive function has no base case in most C programs?**

- [ ] The compiler detects it and raises a compile-time error.
- [ ] The function allocates memory on the heap until it runs out.
- [x] The stack grows indefinitely until it hits the guard page, causing a SIGSEGV.
- [ ] The OS swaps excess stack frames to disk transparently.

*Each recursive call pushes a new frame. With no termination, frames accumulate until the stack exceeds its limit and touches the guard page. The OS sends SIGSEGV, crashing the program.*
