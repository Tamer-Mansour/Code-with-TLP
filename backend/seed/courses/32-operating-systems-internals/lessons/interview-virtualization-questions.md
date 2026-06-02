# Interview Drill: Virtualization Questions

This lesson walks through the most commonly asked virtualization and container questions in systems engineering and SRE interviews, with crisp model answers and the reasoning behind them.

---

## Q1. What is the difference between a Type-1 and Type-2 hypervisor?

**Model answer:** A Type-1 hypervisor runs directly on bare hardware (ESXi, KVM, Hyper-V). A Type-2 runs as an application on a host OS (VirtualBox, VMware Workstation). Type-1 has lower latency because there is no host OS layer between the VMM and hardware; Type-2 is easier to install for desktop use.

**Pitfall to avoid:** Claiming KVM is Type-2 because Linux is running. KVM makes the Linux kernel itself the hypervisor — it is classified as Type-1.

---

## Q2. Why did x86 require hardware extensions for full virtualization?

**Model answer:** Classic x86 has 17 sensitive instructions that are not privileged — they behave differently by privilege level but do not trap. `POPF` and `PUSHF` are the canonical examples: the Interrupt Flag bit is silently masked in ring 3 instead of causing a fault. This breaks the Popek-Goldberg trap-and-emulate model. Intel VT-x (VMX Non-Root mode) and AMD-V fix this by creating a separate guest execution mode where all problematic instructions trigger VM Exits unconditionally.

---

## Q3. What is a VM Exit and why is it expensive?

**Model answer:** A VM Exit is the CPU transition from guest execution (VMX Non-Root) back to the hypervisor. It atomically saves guest register state to the VMCS, loads host state, and jumps to the VMM's exit handler. The cost is ~1,000–3,000 cycles for the transition itself, plus the handler's work. It is expensive because it flushes the pipeline, involves VMCS memory accesses, and may cause TLB invalidations. Hypervisors minimize VM Exits by configuring the VMCS exit bitmap carefully.

---

## Q4. How does EPT improve memory virtualization?

**Model answer:** Without EPT, the VMM maintains shadow page tables that map guest virtual addresses directly to host physical addresses. Every guest page table modification causes a VM Exit so the shadow table can be updated. With EPT, the CPU's MMU performs a two-level hardware walk: guest CR3 → guest physical address → EPT tables → host physical address. The guest modifies its own page tables freely with no VM Exits. TLB misses are slower (up to 24 memory accesses for a 4-level guest + 4-level EPT walk) but the elimination of VM Exit overhead makes EPT a net win for most workloads.

---

## Q5. Containers share the host kernel — what are the security implications?

**Model answer:** The container's attack surface is the entire Linux kernel system call interface. A kernel exploit (e.g., a use-after-free in a socket handler) can grant a container-to-host escape. By contrast, a VM exploit must breach the hypervisor, a much smaller codebase. Mitigations include: seccomp filters (restrict allowed syscalls), AppArmor/SELinux mandatory access control, dropping Linux capabilities, running as a non-root user inside the container, and using runtime sandboxes like gVisor (user-space kernel) or Kata Containers (VM-backed containers).

---

## Q6. What is the IOMMU and when do you need it?

**Model answer:** The IOMMU (Intel VT-d, AMD-Vi) is a hardware unit on the PCIe bus that applies page-table-style address translation to DMA requests from devices. Without it, a device (or a compromised guest with a passed-through device) can DMA into arbitrary host memory. With IOMMU, each device gets its own I/O page table; DMA outside the allowed range triggers a fault. You need it for: (1) safe PCI passthrough to VMs, (2) protecting against physical DMA attacks (Thunderbolt), (3) general hardening in multi-tenant environments.

---

## Q7. What is the difference between namespaces and cgroups?

**Model answer:** Namespaces control **visibility** — a process in a PID namespace sees only the PIDs in its namespace; it cannot see or signal processes outside. cgroups control **resource consumption** — a cgroup with `memory.max=256M` will OOM-kill processes in the group if they exceed 256 MB. They solve orthogonal problems and containers use both: namespaces for isolation, cgroups for resource fairness and limits.

---

## Q8. What is paravirtualization and where is it still used today?

**Model answer:** Paravirtualization modifies the guest OS to call hypercalls instead of executing sensitive instructions, reducing VM Exit overhead. The original Xen PV mode required a patched kernel. Today, **virtio** is the mainstream form: an unmodified kernel uses virtio-net and virtio-blk drivers (paravirtual I/O) while running in full VT-x mode. Every major cloud provider (AWS Nitro, GCP, Azure) uses virtio for network and block I/O, achieving throughputs 5–30× better than emulated devices.

---

## Q9. How does `docker run` actually create a container?

**Model answer (process outline):**

```
1. containerd calls runc
2. runc calls clone() with CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS
3. Child process pivot_root()s into the image layer (overlayfs mount)
4. cgroup hierarchy created; PIDs written to cgroup.procs
5. Capabilities dropped; seccomp profile applied
6. execve() runs the container entrypoint
```

The result is a process tree isolated by namespaces and capped by cgroups, with an overlay filesystem providing the container's root.

---

## Q10. When would you choose a VM over a container?

**Model answer:** Choose a VM when: (a) you need to run a different OS kernel (Windows on Linux host), (b) strong multi-tenant isolation is required (public cloud, financial compliance), (c) you need hardware-level security guarantees against a hostile workload. Choose a container when: packaging dependencies portably, running high-density microservices, maximizing startup speed in CI/CD, or when all tenants are internal/trusted. In practice, modern systems do both — containers inside lightweight VMs (Firecracker, Kata) for cloud-native workloads.
