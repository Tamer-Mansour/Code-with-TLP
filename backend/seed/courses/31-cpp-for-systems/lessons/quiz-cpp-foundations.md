# Quiz: C++ Foundations and the Compilation Model

Test your understanding of the core concepts from this module.

---

**Q1. Which stage of the C++ build pipeline is responsible for expanding `#include` directives and macros?**

- [x] Preprocessor
- [ ] Compiler
- [ ] Assembler
- [ ] Linker

The preprocessor runs before the compiler and performs pure text substitution: it pastes included files in-place and expands `#define` macros. The compiler never sees the raw `#include` directives.

---

**Q2. You define a non-inline function `void helper() {}` in a header file and include that header in three `.cpp` files. What happens when you link?**

- [ ] Everything works fine because include guards prevent duplication.
- [ ] The compiler emits an error for each file that includes the header.
- [x] The linker reports a "multiple definition" error.
- [ ] Only the first definition is used; the others are silently discarded.

Include guards prevent the header from being pasted twice in the *same* translation unit, but each of the three `.cpp` files compiles its own copy of `helper()`. The linker sees three definitions of the same external symbol and refuses to link.

---

**Q3. What is the purpose of `extern "C"` in C++?**

- [ ] It forces a function to have external linkage.
- [ ] It makes a variable accessible from C source files.
- [x] It suppresses C++ name mangling so the symbol can be linked against a C library.
- [ ] It declares a function as `extern` without providing a definition.

C++ mangles function names to support overloading. `extern "C"` disables mangling for the enclosed declarations, making the symbol name match what a C compiler would produce — essential when calling functions from C libraries.

---

**Q4. Which of the following is a declaration but NOT a definition?**

- [ ] `int count = 0;`
- [ ] `void process(int x) { return; }`
- [x] `extern int count;`
- [ ] `class Config { int level; };`

`extern int count;` tells the compiler that `count` exists somewhere, but allocates no storage — it is a pure declaration. All the others allocate storage or generate code (i.e., are definitions as well as declarations).

---

**Q5. A program compiles and links successfully but crashes at runtime with a segmentation fault. Which category does this error fall into?**

- [ ] Compile-time error
- [ ] Linker error
- [x] Runtime error
- [ ] Preprocessor error

A segfault occurs during execution — the program was built successfully. Runtime errors can only be observed by running the program under real (or simulated) conditions, which is why tools like AddressSanitizer are valuable for catching them early.

---

**Q6. In C++, a `const` global variable at namespace scope has which linkage by default?**

- [ ] External linkage, same as a non-const global
- [x] Internal linkage, visible only within its translation unit
- [ ] No linkage, like a local variable
- [ ] External linkage only if marked `extern const`

Unlike C, C++ gives `const` variables at namespace scope **internal linkage** by default. This is why placing `const int MAX = 100;` in a header and including it in multiple `.cpp` files is safe — each TU gets its own private copy and there is no ODR conflict.
