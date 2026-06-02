# Quiz: Dynamic Memory Management

Test your understanding of `new`, `delete`, memory leaks, and related bugs in C++.

---

**Q1. What is the primary difference between `new` and `malloc`?**

- [ ] `new` allocates memory on the stack; `malloc` allocates on the heap.
- [ ] `new` is a function call; `malloc` is an operator.
- [x] `new` calls the object's constructor after allocating memory; `malloc` only allocates raw bytes.
- [ ] `new` always throws on failure; `malloc` always returns `nullptr` on failure.

_`new` combines allocation with construction (and `delete` combines destruction with deallocation), while `malloc`/`free` only manage raw bytes — no constructors or destructors are involved._

---

**Q2. You write `int* arr = new int[10]; delete arr;`. What is the consequence?**

- [ ] Only the first element's destructor is called, but memory is freed correctly.
- [ ] The program safely frees all 10 elements.
- [ ] A compile-time error is produced.
- [x] The behavior is undefined — `delete` should be `delete[]` for array allocations.

_`delete[]` reads an implementation-stored element count to call the right number of destructors; plain `delete` on an array pointer skips that and corrupts heap metadata._

---

**Q3. Which of the following correctly avoids a double-free when copying a resource-owning class?**

- [ ] Using the compiler-generated copy constructor.
- [ ] Setting the pointer to `nullptr` after `delete` in the destructor.
- [ ] Allocating the same size in every copy.
- [x] Implementing a deep-copy copy constructor and copy-assignment operator (Rule of Three/Five).

_The default copy constructor copies the pointer value, causing two objects to own the same memory. A deep copy creates an independent allocation for each object, preventing double-free._

---

**Q4. What does `new (std::nothrow) int[1000]` return when the allocation fails?**

- [ ] It throws `std::bad_alloc`.
- [x] It returns `nullptr`.
- [ ] It calls `std::terminate`.
- [ ] It returns a pointer to a zero-byte block.

_The `std::nothrow` tag selects an overload of `operator new` that catches `bad_alloc` internally and returns `nullptr` instead, allowing the caller to check the result rather than handle an exception._

---

**Q5. Which tool command will detect a heap-use-after-free bug at runtime?**

- [ ] `g++ -Wall -Wextra myprog.cpp`
- [ ] `clang --analyze myprog.cpp`
- [x] `g++ -fsanitize=address -g myprog.cpp && ./a.out`
- [ ] `g++ -O2 myprog.cpp && valgrind --tool=callgrind ./a.out`

_AddressSanitizer (`-fsanitize=address`) poisons freed memory at runtime; any read or write to a freed region is caught immediately with a stack trace. Valgrind with `--leak-check` also detects use-after-free but requires the `memcheck` tool (the default), not `callgrind`._

---

**Q6. Which statement about placement new is TRUE?**

- [ ] You must call `delete` on a pointer returned by placement new.
- [ ] Placement new allocates new memory from the heap every time.
- [ ] Placement new can only be used with trivial types.
- [x] Placement new constructs an object at an address you supply; you must call the destructor explicitly and manage the underlying storage separately.

_Placement new does not allocate memory — it constructs an object at the given address. Because no allocation occurred, calling `delete` would be wrong; you call the destructor explicitly (`obj->~T()`) and release the underlying storage through its original mechanism (e.g., `free`, pool reclaim, etc.)._
