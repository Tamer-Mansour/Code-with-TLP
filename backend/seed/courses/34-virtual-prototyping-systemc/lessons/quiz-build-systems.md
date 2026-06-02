# Quiz: Build Systems, Compilers, and Make

**Q1. Which compilation stage is responsible for resolving the `#include <systemc.h>` directive and expanding macros?**

- [x] Preprocessing
- [ ] Compilation
- [ ] Assembly
- [ ] Linking

_The preprocessor runs first and handles all `#` directives, producing an expanded `.i` file before any code analysis happens._

---

**Q2. A developer gets the error `undefined reference to 'sc_start'`. What is the most likely cause?**

- [ ] The `-I` include path for `systemc.h` is missing.
- [ ] The source file contains a syntax error.
- [x] The `-lsystemc` linker flag is missing or placed before the object files.
- [ ] The `-g` debug flag was omitted.

_`undefined reference` is a linker error, not a compiler error. The linker cannot find the definition of `sc_start` because `libsystemc` was not linked, or was listed before the object files that reference it._

---

**Q3. What does the `-fPIC` compiler flag do, and when is it required?**

- [ ] It enables profile-guided optimisation.
- [ ] It disables position-independent code for speed.
- [x] It generates position-independent code, required for shared libraries.
- [ ] It forces the preprocessor to inline all headers.

_Shared libraries are mapped to arbitrary virtual addresses, so their code must not contain absolute addresses. `-fPIC` emits relocatable instruction sequences to satisfy this requirement._

---

**Q4. In a Makefile, what happens if you indent a recipe line with spaces instead of a TAB character?**

- [ ] The recipe runs but the output is suppressed.
- [ ] The recipe is silently skipped.
- [x] `make` reports a "missing separator" error and aborts.
- [ ] `make` automatically converts spaces to a TAB.

_GNU make requires recipes to start with a literal TAB character. Spaces are not equivalent and trigger a parse error._

---

**Q5. You modify `cpu_model.h`, which is included by both `cpu_model.cpp` and `main.cpp`. With a correct Makefile (using `-MMD` dependency files), which files will be recompiled?**

- [ ] Only `cpu_model.cpp`
- [ ] Only `main.cpp`
- [x] Both `cpu_model.cpp` and `main.cpp`, and then `sim` is relinked.
- [ ] Neither; header changes never trigger recompilation.

_The `-MMD` flag generates `.d` files listing all included headers as prerequisites. When `cpu_model.h` is newer than either `.o`, both are rebuilt and the final link step runs again._

---

**Q6. What is the primary advantage of a static library over a shared library for a deliverable SystemC simulator?**

- [ ] It uses less disk space.
- [ ] It loads faster because of shared pages in the OS page cache.
- [ ] It allows runtime library updates without relinking.
- [x] It produces a self-contained executable with no runtime library dependency.

_A statically linked simulator embeds all library code into the binary, so it runs on any compatible host without requiring `libsystemc.so` to be installed._
