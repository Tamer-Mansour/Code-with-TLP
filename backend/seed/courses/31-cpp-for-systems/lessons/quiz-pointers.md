# Quiz: Pointers Deep Dive

Test your understanding of pointer semantics, arithmetic, const qualifiers, and null pointer conventions.

---

**Q1. Given `int arr[] = {10, 20, 30}` and `int* p = arr;`, what does `*(p + 2)` evaluate to?**

- [ ] 10
- [ ] 20
- [x] 30
- [ ] The address of arr[2]

`p + 2` advances the pointer by `2 × sizeof(int)` bytes, landing on `arr[2]` which holds 30. Dereferencing gives the value, not the address.

---

**Q2. On a 64-bit platform, what is `sizeof(double*)`?**

- [ ] 4
- [x] 8
- [ ] 16
- [ ] Same as `sizeof(double)`, which is 8 by coincidence but for different reasons

All pointers on a 64-bit system are 8 bytes regardless of the type they point to, because they store a 64-bit virtual address. The pointed-to type determines arithmetic stride, not pointer size.

---

**Q3. Which declaration makes the pointer itself constant (cannot be reseated) while the data it points to remains mutable?**

- [ ] `const int* p`
- [x] `int* const p`
- [ ] `const int* const p`
- [ ] `int const p`

`int* const p` — `const` to the right of `*` constrains the pointer. `const int* p` constrains the data. `const int* const p` constrains both.

---

**Q4. Why should `nullptr` be preferred over `NULL` or `0` in C++?**

- [ ] `nullptr` is faster at runtime
- [ ] `NULL` was removed from C++11
- [x] `nullptr` has type `std::nullptr_t` and does not implicitly convert to `int`, making overload resolution unambiguous
- [ ] `nullptr` automatically frees memory when assigned

`nullptr` solves the classic overload problem: `foo(0)` calls `foo(int)`, but `foo(nullptr)` unambiguously calls `foo(int*)`. `NULL` is typically `0` or `0L` in C++, which has integer type.

---

**Q5. What happens when an array name is used as a function argument, such as `void f(int arr[])`?**

- [ ] The entire array is copied onto the stack
- [x] The array decays to a pointer to its first element; size information is lost
- [ ] A compile error occurs because arrays cannot be passed to functions
- [ ] The function receives a reference to the original array with full size information

Array-to-pointer decay occurs at the call site. Inside `f`, `sizeof(arr)` yields the pointer size (typically 8), not the array's total byte count.

---

**Q6. Given `int x = 5; int* p = &x; int** pp = &p;`, which expression modifies `x` to 99?**

- [ ] `*pp = 99`
- [ ] `pp = 99`
- [x] `**pp = 99`
- [ ] `&pp = 99`

`*pp` dereferences `pp` to get `p` (the inner pointer). `**pp` dereferences `p` to reach `x`. Writing to `**pp` writes to `x`. Writing to `*pp` would reseat the inner pointer `p`, not touch `x`.
