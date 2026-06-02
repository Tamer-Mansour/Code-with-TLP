# Interview Drill: Stack vs Heap Questions

This lesson walks through the most commonly asked stack and heap interview questions with model answers. These questions appear in systems programming, OS, and backend engineering interviews. For each question, read the prompt, formulate your own answer, then compare with the model response.

---

## Q1: What is the difference between stack and heap memory?

**Model answer:**

The **stack** is automatically managed — it grows when a function is called and shrinks when it returns, with allocation/deallocation costing a single pointer adjustment. It is fast but small (typically 1–8 MB).

The **heap** is manually managed (or GC-managed). Allocation (`malloc`, `new`) searches a free list and may call the OS; it is slower but can be gigabytes in size. Heap memory persists until explicitly freed.

**Crisp one-liner:** "Stack is fast and automatic but size-limited; heap is flexible but requires manual management."

---

## Q2: Can a local variable outlive the function it was declared in?

**Model answer:**

Not if it's stack-allocated — it is destroyed when the function returns. Returning a pointer to a stack local is undefined behavior:

```c
int *bad(void) {
    int x = 5;
    return &x;   // UB: x is gone after return
}
```

A local can conceptually outlive its function only if it is stored on the heap (allocated with `malloc`/`new`) or is a `static` local (which lives in the BSS/data segment for the entire program lifetime).

---

## Q3: What causes a stack overflow, and how do you fix it?

**Model answer:**

A stack overflow happens when the call stack exceeds its size limit — usually from infinite or excessively deep recursion, or from a single function allocating a huge local array. The OS detects the violation via a guard page and terminates the process with SIGSEGV.

Fixes:
- Add or correct the base case for recursion.
- Convert deep recursion to iteration with an explicit stack.
- Move large buffers to the heap with `malloc`.
- Use tail-call optimization if the language/compiler supports it.

---

## Q4: What is a memory leak and how do you detect one?

**Model answer:**

A memory leak is heap memory that is allocated but never freed, and all pointers to it have been lost — so it cannot be reclaimed until the process exits. In a long-running process, leaks accumulate and eventually exhaust memory.

Detection:
- **Valgrind** (`--leak-check=full`) reports exact allocation sites.
- **AddressSanitizer** (`-fsanitize=address`) catches leaks, use-after-free, and buffer overflows at near-native speed.
- **Heap profilers** (heaptrack, massif) track allocation trends over time.

---

## Q5: What is the difference between a dangling pointer and a null pointer?

**Model answer:**

A **null pointer** holds the value `0` (or `NULL`). Dereferencing it causes an immediate, predictable crash (SIGSEGV), making the bug easy to locate.

A **dangling pointer** holds a formerly valid address whose memory has been freed or gone out of scope. Dereferencing it is undefined behavior — it may silently read corrupted data, crash non-deterministically, or enable security exploits (use-after-free). Dangling pointers are far harder to diagnose.

Best practice: after calling `free(p)`, immediately set `p = NULL`.

---

## Q6: Why is struct layout affected by alignment, and how do you minimize wasted space?

**Model answer:**

CPUs access memory most efficiently when data is naturally aligned (address is a multiple of its size). To guarantee this, compilers insert **padding bytes** between struct members. A struct's total size is also rounded up to a multiple of its most-aligned member.

To minimize padding, **sort members from largest to smallest alignment**:

```c
// Wasteful: 12 bytes
struct Bad  { char a; int b; char c; };

// Optimal: 8 bytes
struct Good { int b; char a; char c; };
```

Use `sizeof` and `offsetof` to verify the layout; never guess.

---

## Q7: Where do global variables live, and are they thread-safe?

**Model answer:**

Initialized non-zero globals live in the `.data` segment; zero-initialized (or uninitialized) globals live in the `.bss` segment. Both exist for the entire process lifetime and are **shared among all threads** — so reads and writes to globals require synchronization (mutex, atomic) to be thread-safe. Plain global access is not thread-safe.

---

## Quick Reference Card

| Question | Key point |
|---|---|
| Stack vs heap | Speed + automatic vs size + manual |
| Stack overflow | Guard page hit; fix with base case or iteration |
| Memory leak | Lost pointer to heap; detect with Valgrind/ASan |
| Dangling pointer | Freed/gone address; set to NULL after free |
| Struct padding | Align members largest-first to minimize |
| Globals | .data/.bss; shared — not thread-safe without sync |
