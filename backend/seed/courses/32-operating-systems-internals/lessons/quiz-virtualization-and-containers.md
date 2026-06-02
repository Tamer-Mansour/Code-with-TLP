# Quiz: Virtualization, Containers, and Hardware Support

Test your understanding of hypervisors, hardware virtualization extensions, containers, and the Linux primitives that power them.

---

**Q1. Which statement correctly describes Intel VT-x's VMX Non-Root mode?**

- [ ] The guest OS runs in ring 1 and sensitive instructions are emulated by a binary translator.
- [x] The guest OS runs at full ring-0 privilege but certain events automatically trigger a VM Exit to the hypervisor.
- [ ] The guest OS runs entirely in user space (ring 3) with no hardware acceleration.
- [ ] VMX Non-Root mode is only activated when Extended Page Tables (EPT) are enabled.

_VMX Non-Root mode gives the guest unrestricted ring-0 execution; the VMCS exit bitmap defines which events cause automatic VM Exits, eliminating the need for ring compression or binary translation._

---

**Q2. A hypervisor uses shadow page tables instead of EPT. What is the main performance cost?**

- [ ] Every TLB miss requires two hardware page-table walks instead of one.
- [ ] The guest cannot use more than 4 GB of physical memory.
- [x] Every guest page-table write causes a VM Exit so the VMM can update the shadow table.
- [ ] Shadow page tables disable the CPU's hardware prefetcher.

_Without EPT, the VMM write-protects the guest's page tables. Any guest write faults, causing a VM Exit and a synchronization pass. EPT eliminates this by handling GPA→HPA translation entirely in hardware._

---

**Q3. Which of the following is a sensitive but NON-privileged instruction on classic (pre-VT-x) x86, making pure trap-and-emulate impossible?**

- [ ] `HLT` (halt the processor)
- [ ] `LGDT` (load global descriptor table register)
- [x] `POPF` (pop flags register — silently drops IF bit in ring 3)
- [ ] `MOV CR3, RAX` (write page-table base register)

_`POPF` is the textbook example: in ring 3 it silently ignores the Interrupt Flag bit instead of faulting, so the VMM never gets control and the guest reads incorrect flag state._

---

**Q4. What is the primary role of the IOMMU in a virtualized system?**

- [ ] It translates guest virtual addresses to guest physical addresses faster than the CPU MMU.
- [ ] It provides a second TLB dedicated to hypervisor page tables.
- [ ] It encrypts DMA transfers between devices and RAM.
- [x] It applies per-device address translation and access control to DMA requests, enabling safe PCI passthrough.

_The IOMMU enforces that a device's DMA can only reach memory regions explicitly mapped for that device. This prevents a compromised guest (with a passed-through device) from writing to another guest's or the host's memory._

---

**Q5. A container is started with `docker run --memory=512m`. What Linux mechanism enforces this limit?**

- [ ] A PID namespace that kills processes exceeding the memory budget.
- [ ] A mount namespace that restricts `mmap()` calls to a 512 MB virtual address range.
- [x] A cgroup with `memory.max` set to 536870912 bytes; the kernel's OOM killer targets processes in that cgroup if the limit is exceeded.
- [ ] The container runtime intercepts `malloc()` calls and returns `ENOMEM` after 512 MB.

_cgroups (v2: `memory.max`, v1: `memory.limit_in_bytes`) account for all physical pages charged to the group. When the limit is hit, the in-cgroup OOM killer fires — only processes in that cgroup are candidates._

---

**Q6. Which combination is used by AWS Firecracker to achieve both fast startup (like containers) and strong isolation (like VMs)?**

- [ ] Containers with a gVisor kernel interposed between the app and the host kernel.
- [ ] Full KVM VMs running a complete Ubuntu OS image.
- [x] Lightweight VMs using a minimal VMM and a stripped-down kernel, booting in ~125 ms with hardware (KVM/VT-x) isolation boundaries.
- [ ] Xen paravirtual domains with no hardware virtualization extensions.

_Firecracker is a microVM VMM written in Rust. It uses KVM (VT-x/AMD-V) for isolation but boots a tiny kernel with minimal devices, achieving ~125 ms cold-start while maintaining VM-level security for multi-tenant workloads._
