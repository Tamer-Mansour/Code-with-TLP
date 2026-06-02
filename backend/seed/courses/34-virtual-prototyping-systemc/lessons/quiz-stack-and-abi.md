# Quiz: The Stack, Calling Conventions, and ABI

Test your understanding of stack mechanics, calling conventions, and ABI concepts covered in this module.

---

**Q1. On a downward-growing stack, what happens when a PUSH instruction executes?**

- [ ] SP is incremented, then the value is written at the new SP address.
- [x] SP is decremented, then the value is written at the new SP address.
- [ ] The value is written at the current SP address, then SP is decremented.
- [ ] SP is decremented and the value is discarded; reading back requires a POP.

_A PUSH on a downward-growing stack always decrements SP first (to claim a new slot) and then writes the value. Writing before decrementing would overwrite the most recently pushed value._

---

**Q2. In the x86-64 System V ABI, which registers carry the first three integer arguments to a function call?**

- [ ] `RAX`, `RBX`, `RCX`
- [ ] `RCX`, `RDX`, `R8`
- [x] `RDI`, `RSI`, `RDX`
- [ ] `R8`, `R9`, `R10`

_The x86-64 System V ABI argument order for integer/pointer arguments is: RDI (1st), RSI (2nd), RDX (3rd), RCX (4th), R8 (5th), R9 (6th). The Windows x64 ABI uses a different order (RCX, RDX, R8, R9)._

---

**Q3. Which of the following best describes a "callee-saved" register?**

- [ ] A register the callee may freely overwrite without saving it first.
- [ ] A register used only to pass arguments to the callee.
- [x] A register the callee must save and restore if it uses it, so the caller sees its original value after the call.
- [ ] A register that holds the return address of the current function.

_Callee-saved (non-volatile) registers are preserved across function calls from the caller's perspective. If a callee needs to use them, it must push them in the prologue and pop them in the epilogue. Contrast with caller-saved (volatile) registers, which the callee may freely clobber._

---

**Q4. An ABI break is more dangerous than an API break primarily because:**

- [ ] ABI breaks always require rewriting source code in a new language.
- [ ] API breaks are caught only at link time, while ABI breaks are caught at compile time.
- [x] ABI breaks compile silently but cause crashes or silent data corruption at runtime.
- [ ] ABI breaks only affect floating-point operations.

_An API break prevents compilation. An ABI break — such as changing a struct's field layout or the size of `long` — allows the source to compile and link successfully, but the resulting binary reads fields at wrong offsets, causing unpredictable runtime behavior that is very hard to diagnose._

---

**Q5. A function uses `char buf[4096]` as a local variable. What stack risk does this introduce in an embedded system with a 4 KB stack?**

- [ ] No risk; the compiler moves large locals to the heap automatically.
- [ ] The variable is allocated in BSS instead, so the stack is unaffected.
- [x] The single function call immediately consumes the entire stack, and any subsequent call or interrupt handler will overflow.
- [ ] The compiler refuses to compile the function if the local is larger than the stack.

_A large local variable is allocated in the stack frame. A 4 KB local on a 4 KB stack leaves zero room for the return address, saved registers, or any nested calls, resulting in an immediate stack overflow on the first call to this function._

---

**Q6. What is the purpose of the "stack canary" protection?**

- [ ] It allocates a guard page below the stack to catch overflow with a page fault.
- [ ] It randomizes the stack base address to make exploitation harder.
- [ ] It copies all return addresses to a read-only shadow stack in hardware.
- [x] It places a random value between local variables and the return address; a mismatch detected on return triggers an immediate abort, catching stack buffer overflows.

_Stack canaries (enabled by `-fstack-protector` and variants) insert a random sentinel value at a fixed offset in the frame. Before executing `RET`, the epilogue checks that the canary is unchanged. An overflow that reaches the return address must pass through and corrupt the canary, triggering the abort before control is hijacked._
