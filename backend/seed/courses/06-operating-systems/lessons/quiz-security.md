# Quiz: OS Security and Protection

**Q1. On a typical x86-64 Linux system, user applications run in which protection ring?**

- [ ] Ring 0
- [ ] Ring 1
- [ ] Ring 2
- [x] Ring 3

**Q2. An Access Control List (ACL) corresponds to which dimension of the access control matrix?**

- [ ] A row — listing all objects a given subject can access
- [x] A column — listing all subjects that can access a given object and their permissions
- [ ] A diagonal — listing each subject's access to its own objects only
- [ ] A transposed matrix — swapping subjects and objects for efficiency

**Q3. A classic stack buffer overflow attack typically aims to overwrite:**

- [ ] The heap metadata header to corrupt subsequent malloc() calls
- [ ] The process's open file descriptor table
- [x] The saved return address on the stack to redirect execution to attacker-controlled code
- [ ] The program's global variables section (.bss) to bypass canary checks

**Q4. Return-Oriented Programming (ROP) was developed to bypass which specific defense?**

- [ ] ASLR (Address Space Layout Randomization)
- [ ] Stack canaries
- [x] NX/DEP — the Non-Executable stack/heap that prevents injected shellcode from running
- [ ] SELinux mandatory access control policies

**Q5. Address Space Layout Randomization (ASLR) is less effective on 32-bit processes than 64-bit processes because:**

- [ ] 32-bit processes have no stack or heap, so there is nothing to randomize
- [ ] The NX bit is not available in 32-bit mode, making ASLR irrelevant
- [x] 32-bit virtual address space provides far less entropy (about 16 bits vs 128+ bits), making brute-force guessing feasible
- [ ] 32-bit Linux kernels do not implement ASLR at all

**Q6. Stack canaries detect buffer overflows by:**

- [ ] Scanning all function parameters for out-of-bounds pointers before the call
- [x] Placing a random value between local variables and the saved return address, then verifying it is unchanged before returning
- [ ] Using the MMU to mark stack memory read-only during function execution
- [ ] Comparing the current stack pointer against a minimum allowed value on every instruction
