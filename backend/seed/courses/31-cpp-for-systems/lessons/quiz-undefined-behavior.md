# Quiz: Undefined Behavior, Crashes, and Memory Errors

**Q1. Which of the following is undefined behavior in C++?**

- [ ] Adding two `unsigned int` values that wrap past `UINT_MAX`
- [x] Adding two `int` values that overflow past `INT_MAX`
- [ ] Dividing an unsigned integer by 2
- [ ] Casting a `void*` back to the pointer type it was originally converted from

Signed integer overflow is explicitly undefined behavior; unsigned overflow is well-defined (wraps modulo 2^N).

---

**Q2. A programmer writes `if (ptr != nullptr) { *ptr = 5; }` but the compiler eliminates the null check in the optimized build. What most likely caused this?**

- [ ] The compiler has a bug in its null-pointer optimization pass
- [ ] The check was written after an earlier dereference of `ptr` in the same scope
- [x] An earlier unconditional dereference of `ptr` in the same function proved to the optimizer that `ptr` cannot be null
- [ ] The `-O2` flag always removes null checks to improve performance

If `ptr` was unconditionally dereferenced earlier, the optimizer proves it cannot be null (a null dereference would be UB, which never happens by assumption), making the subsequent check dead code.

---

**Q3. What is the primary difference between a stack overflow and a stack buffer overflow?**

- [ ] Stack overflow is a security vulnerability; stack buffer overflow is always benign
- [ ] Stack buffer overflow exhausts the total stack space; stack overflow corrupts a frame
- [x] Stack overflow exhausts the total call stack (usually via deep recursion); stack buffer overflow corrupts data within a single frame by writing past a local buffer
- [ ] They are two names for the same event

A stack overflow is about running out of total stack space. A stack buffer overflow is a bounds violation within one frame that overwrites adjacent frame data.

---

**Q4. Which sanitizer is best suited to detecting a read from an uninitialized local variable?**

- [ ] AddressSanitizer (ASan)
- [x] MemorySanitizer (MSan)
- [ ] ThreadSanitizer (TSan)
- [ ] UndefinedBehaviorSanitizer (UBSan)

MemorySanitizer tracks which bytes have been written and reports any branch or value that depends on uninitialized memory. ASan catches memory region violations, not uninitialized reads.

---

**Q5. Given the following code, what does a conforming C++ compiler guarantee about the output?**

```cpp
int x;
std::cout << x << "\n";
```

- [ ] The output will be 0, because the OS zero-initializes all memory
- [ ] The output will be whatever was previously in that memory address
- [ ] The program will crash with a segfault
- [x] Nothing — reading an uninitialized variable is undefined behavior; any output is possible

Reading an uninitialized automatic variable is UB. The standard makes no guarantee: the value could appear to be 0, garbage, or the compiler could generate completely different code.

---

**Q6. A security engineer wants to prevent stack buffer overflows from being exploited to redirect control flow. Which compiler feature addresses this most directly?**

- [ ] `-fPIE` (position-independent executable)
- [ ] `-D_FORTIFY_SOURCE=2`
- [x] `-fstack-protector-strong` (stack canaries)
- [ ] `-fsanitize=address`

Stack canaries place a random value between local buffers and the return address. Before returning, the compiler checks the canary; if overwritten, the program aborts instead of jumping to attacker-controlled code. ASLR (`-fPIE`) and FORTIFY_SOURCE add complementary mitigations but do not directly protect the return address via canary.
