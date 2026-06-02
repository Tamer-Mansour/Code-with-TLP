# Quiz: Memory Model: Stack vs Heap

Test your understanding of how C++ programs manage memory across the stack, heap, and static segments.

---

**Q1. Where does a zero-initialized global variable `int counter;` live?**

- [ ] On the stack, because it has no explicit value
- [ ] In the `.data` segment of the binary
- [x] In the `.bss` segment, which the OS zeroes at load time
- [ ] On the heap, because its size is not known until runtime

The `.bss` segment holds all zero-initialized globals and statics. The OS guarantees they are zero before `main` runs, and the binary stores only the segment size — not the actual bytes.

---

**Q2. What happens when a local variable's scope ends in C++?**

- [ ] The memory is immediately returned to the OS
- [ ] The variable's destructor is called only if the type is a class
- [x] The variable's destructor is called and its stack storage is reclaimed in reverse declaration order
- [ ] The variable lives until the program exits, like a static variable

All local variables — including those of built-in types — are destroyed in reverse declaration order when their scope ends. For built-in types the destructor is trivial (no-op), but storage is reclaimed immediately.

---

**Q3. On x86-64 Linux (System V ABI), how are the first six integer arguments passed to a function?**

- [ ] All pushed onto the stack before the CALL instruction
- [x] In registers RDI, RSI, RDX, RCX, R8, R9
- [ ] In registers RCX, RDX, R8, R9, and two are pushed on the stack
- [ ] In a struct placed at the top of the stack

The System V ABI passes the first six integer/pointer arguments in the listed registers. Additional arguments spill to the stack. The Windows x64 ABI is different: it uses RCX, RDX, R8, R9 for the first four.

---

**Q4. Which of the following is the most likely cause of a stack overflow?**

- [ ] Calling `delete` on a null pointer
- [ ] Allocating a large object with `new`
- [x] Unbounded or very deep recursion filling the stack with frames
- [ ] Writing past the end of a heap buffer

Each recursive call pushes a new stack frame. Without a reachable base case — or with extremely deep recursion — the stack pointer crosses the guard page, triggering a segfault / access violation.

---

**Q5. A developer writes `const char* s = "hello";` and later tries `s[0] = 'H';`. What happens?**

- [ ] The character is changed successfully because `s` is a pointer
- [ ] The compiler rejects it because `s[0]` is not an lvalue
- [x] Undefined behaviour — likely a segfault because string literals live in read-only memory
- [ ] The write succeeds on Linux but fails on Windows

String literals live in `.rodata`, which is mapped read-only. Casting away `const` and writing is undefined behaviour; in practice the OS raises SIGSEGV when the process attempts to write to a read-only page.

---

**Q6. Which C++ mechanism best avoids memory leaks when allocating objects on the heap?**

- [ ] Calling `delete` at the start of every function that allocates
- [ ] Using `static` storage so the object lives for the whole program
- [ ] Declaring the object `volatile` so the compiler does not optimize it away
- [x] Wrapping the allocation in a RAII type such as `std::unique_ptr` or `std::vector`

RAII types store ownership of the heap resource inside a stack object. When the stack object goes out of scope (including on exception or early return), its destructor calls `delete` automatically — eliminating the need for manual cleanup on every code path.
