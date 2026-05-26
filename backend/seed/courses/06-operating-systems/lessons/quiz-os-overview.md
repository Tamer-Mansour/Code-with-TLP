# Quiz: OS Overview

**Q1. What privilege ring does the Linux kernel run in on x86-64?**

- [ ] Ring 3
- [ ] Ring 1
- [x] Ring 0
- [ ] Ring 2

**Q2. Which event does NOT cause a transition from user mode to kernel mode?**

- [ ] A hardware interrupt from a network card
- [ ] A page fault exception
- [x] A function call within the same process
- [ ] A `read()` system call

**Q3. What is the primary purpose of the dual-mode (user/kernel) hardware mechanism?**

- [ ] To speed up memory allocation by keeping the allocator in ring 1
- [ ] To enable multi-core parallelism through per-core privilege levels
- [x] To protect the OS kernel and other processes from faulty or malicious user code
- [ ] To compress disk data transparently before it reaches user space

**Q4. Which of the following is a system call on Linux, not a C library wrapper?**

- [ ] `printf()`
- [ ] `strlen()`
- [x] `mmap()`
- [ ] `malloc()`

**Q5. The Linux vDSO mechanism allows certain calls like `clock_gettime` to run without a full mode switch. This works because:**

- [ ] The kernel pre-computes the time and hard-codes it into the binary
- [ ] The real-time clock is mapped into I/O space accessible from ring 3
- [x] The kernel writes current-time data into a shared memory page that processes can read directly
- [ ] The vDSO runs in ring 1, which has permission to read the hardware timer

**Q6. A monolithic kernel places device drivers in:**

- [x] Ring 0, the same address space as the rest of the kernel
- [ ] Ring 3, in isolated user-space processes
- [ ] A separate hardware partition enforced by IOMMU
- [ ] A virtual machine hypervisor layer beneath the OS
