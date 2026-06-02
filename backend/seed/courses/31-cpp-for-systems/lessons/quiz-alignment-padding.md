# Quiz: Memory Layout, Alignment, and Padding

**Q1. Given the following struct on a 64-bit platform, what is `sizeof(S)`?**

```cpp
struct S {
    char   a;
    int    b;
    char   c;
};
```

- [ ] 6
- [ ] 8
- [x] 12
- [ ] 16

After `char a` (offset 0, size 1), 3 bytes of padding are inserted so `int b` lands at offset 4 (alignment 4). After `char c` at offset 8, 3 bytes of tail padding bring the total to 12 (a multiple of 4, the struct's alignment).

---

**Q2. Which reordering of the members of the struct above produces the smallest `sizeof`?**

```cpp
struct S { char a; int b; char c; };
```

- [ ] `int b; char a; char c;` — sizeof 8
- [x] `int b; char a; char c;` — sizeof 8 (correct, 4+1+1+2pad=8)
- [ ] `char a; char c; int b;` — sizeof 8
- [ ] Order does not matter; sizeof is always 12

Both `int b; char a; char c;` and `char a; char c; int b;` produce sizeof 8. Placing the `int` first (or two `char`s before the `int`) eliminates the 3-byte internal gap. The key insight is that grouping same-sized or descending-size members removes internal padding.

---

**Q3. What does `alignof(double)` return on a typical 64-bit platform?**

- [ ] 4
- [x] 8
- [ ] 16
- [ ] It is implementation-defined and has no typical value

`double` is 8 bytes in size and requires 8-byte alignment on virtually all 64-bit platforms (x86-64, ARM64, etc.) per their System V or ARM ABIs.

---

**Q4. Which of the following is the correct, portable way to read a `float`'s raw bits as a `uint32_t` in C++?**

- [ ] `uint32_t b = *(uint32_t*)(&f);`
- [ ] `union { float f; uint32_t u; } p; p.f = f; return p.u;`
- [x] `uint32_t b; std::memcpy(&b, &f, sizeof(b));`
- [ ] `uint32_t b = static_cast<uint32_t>(f);`

The pointer cast violates the strict aliasing rule (UB). The union pun is UB in standard C++ (though a GCC extension). The `static_cast` performs a numeric conversion, not a bit-reinterpretation. Only `memcpy` is well-defined and compiles to a single instruction with optimization enabled.

---

**Q5. What is the primary cause of "false sharing" in a multithreaded program?**

- [ ] Two threads reading the same variable simultaneously
- [ ] A lock being held by one thread while another tries to acquire it
- [x] Two threads writing to different variables that reside in the same 64-byte cache line
- [ ] A thread writing a value that is not aligned to its natural boundary

False sharing occurs when independently-written variables land in the same cache line. Every write by one core invalidates the entire line in all other cores' caches, forcing a re-fetch even though the logically distinct variable was not touched. The fix is to pad each hot variable to a full cache-line width (64 bytes).

---

**Q6. Which keyword combination lets you declare a struct member aligned to 32 bytes in standard C++11?**

- [ ] `__attribute__((aligned(32))) float data[8];`
- [x] `alignas(32) float data[8];`
- [ ] `#pragma align(32) float data[8];`
- [ ] `aligned(32) float data[8];`

`alignas(N)` is the standard C++11 keyword for specifying alignment. `__attribute__((aligned(N)))` is a GCC/Clang extension that predates the standard. `#pragma align` and bare `aligned()` are not valid C++ syntax.
