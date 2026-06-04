# Quiz: Virtualization and Containerization

**Q1. What is the key difference between a Type 1 and Type 2 hypervisor?**

- [ ] Type 1 supports only Linux guests; Type 2 supports Windows guests
- [x] Type 1 runs directly on bare hardware; Type 2 runs atop a host operating system
- [ ] Type 1 uses software binary translation; Type 2 uses hardware-assisted virtualization
- [ ] Type 1 uses containers; Type 2 uses full virtual machines

**Q2. Classic x86 processors presented a virtualization challenge because:**

- [ ] They lacked a memory management unit (MMU)
- [ ] Ring 0 instructions always trapped to the OS without exception
- [x] Some sensitive instructions (like POPF) behaved differently in user mode without trapping, breaking trap-and-emulate
- [ ] x86 CPUs ran too fast for the hypervisor to intercept instructions

**Q3. Intel VT-x introduces VMX root mode and VMX non-root mode. When does a VMEXIT occur?**

- [ ] Every time the guest OS reads a memory address
- [x] When the guest executes a sensitive operation (e.g., I/O, certain privilege-level instructions) that the VMCS is configured to intercept
- [ ] Periodically on a fixed timer regardless of what the guest is doing
- [ ] Only when the guest OS explicitly calls a hypercall instruction

**Q4. Extended Page Tables (EPT) improve virtualization performance by:**

- [ ] Compressing guest memory to fit more VMs per host
- [ ] Eliminating the need for the guest OS to manage page tables at all
- [x] Adding a hardware second-level page table walk so that guest page table modifications no longer require VMEXITs
- [ ] Encrypting all guest memory accesses to prevent cross-VM data leaks

**Q5. Which Linux kernel mechanism is primarily responsible for resource limitation (CPU, memory) in containers?**

- [ ] Namespaces
- [ ] eBPF programs
- [x] Control groups (cgroups)
- [ ] seccomp filters

**Q6. Para-virtualization differs from full hardware virtualization in that:**

- [ ] Para-virtualization requires no hypervisor — containers provide the isolation
- [ ] Para-virtualization runs guest code in ring 0 without any interception
- [x] The guest OS is modified to make explicit hypercalls instead of issuing privileged instructions that would trap
- [ ] Para-virtualization uses shadow page tables exclusively and does not support EPT/NPT
