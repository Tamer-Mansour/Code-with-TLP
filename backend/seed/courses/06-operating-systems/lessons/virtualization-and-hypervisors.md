# Virtualization and Hypervisors

**Virtualization** creates the illusion of multiple independent computers on a single physical machine. A **hypervisor** (Virtual Machine Monitor, or VMM) sits between the hardware and the guest operating systems, managing CPU, memory, and device access for each virtual machine (VM).

## Type 1 vs. Type 2 Hypervisors

```
Type 1 (Bare-Metal)                Type 2 (Hosted)
────────────────────               ─────────────────────
Guest OS A  Guest OS B             Guest OS A  Guest OS B
     └──────┘                           └──────┘
      Hypervisor (ring 0)               Host OS Hypervisor
      Physical Hardware                 Host OS (ring 0)
                                        Physical Hardware
```

| Property | Type 1 | Type 2 |
|----------|--------|--------|
| Examples | VMware ESXi, Microsoft Hyper-V, Xen | VirtualBox, VMware Workstation, QEMU |
| Performance | Near-native | Moderate overhead from host OS |
| Use case | Data centers, cloud (AWS EC2, Azure VMs) | Developer workstations, testing |
| Latency | Low (direct hardware access) | Higher (host OS scheduler involved) |

## The Virtualization Challenge: Sensitive Instructions

The core problem: guest OS code executes in ring 3 (or ring 1 in classic x86), but it issues **privileged instructions** (like loading CR3, modifying the IDT, disabling interrupts) that must be controlled by the hypervisor, not executed directly.

A CPU instruction is **virtualizable** if attempting it in non-privileged mode causes a trap (which the hypervisor can intercept). The classic x86 architecture had 17 instructions that were **sensitive but not privileged** — they behaved differently in user mode without trapping, making pure trap-and-emulate impossible.

## Trap-and-Emulate

On architectures with full trap support, the hypervisor uses trap-and-emulate:

```
Guest executes privileged instruction
         |
         v (hardware trap → hypervisor)
Hypervisor inspects the instruction
         |
         v
Hypervisor emulates the effect safely
(e.g., updates a shadow copy of guest's CR3)
         |
         v
Hypervisor returns to guest — guest is unaware
```

This works perfectly on SPARC and IBM mainframes, which were designed with virtualization in mind. x86 required workarounds.

## Binary Translation (Software VMM)

VMware's original solution (1999): the hypervisor dynamically rewrites guest kernel code. Sensitive non-trapping instructions are replaced with safe equivalents or calls into the VMM, before the guest runs. This is done at runtime, one basic block at a time, and cached for reuse.

- Performance: ~10–20% overhead on typical workloads
- No hardware changes needed
- Compatible with all x86 guest OSes

## Hardware-Assisted Virtualization: Intel VT-x / AMD-V

Modern processors solve the x86 virtualization gap with dedicated hardware support:

- Intel introduced **VT-x** (Virtualization Technology) in 2005
- AMD introduced **AMD-V** (SVM) in 2006

New CPU execution modes:
- **VMX root mode** (ring 0): the hypervisor runs here with full hardware access
- **VMX non-root mode**: guest OS runs here, appearing to have ring 0 privileges but actually trapped on sensitive operations

Key instructions:
```
VMLAUNCH  - start a VM
VMRESUME  - resume a paused VM
VMEXIT    - hardware-triggered return to hypervisor
VMREAD/VMWRITE - read/write the VMCS (VM Control Structure)
```

The **VMCS** (Virtual Machine Control Structure) records what triggers a VMEXIT (e.g., I/O instructions, page faults, CPUID) and stores the VM's CPU state. A VMEXIT/VMRESUME cycle takes ~1000–4000 CPU cycles — far cheaper than binary translation.

## Memory Virtualization

Each guest OS manages its own page tables (guest virtual → guest physical), but the hypervisor must also manage the mapping from guest-physical to machine-physical addresses.

### Shadow Page Tables (Software)

The hypervisor maintains a **shadow page table** that maps guest-virtual directly to machine-physical addresses. When the guest modifies its own page tables, the hypervisor intercepts the write and updates the shadow tables. Expensive: every guest page table modification triggers a VMEXIT.

### Nested/Extended Page Tables (Hardware)

Intel's **EPT** (Extended Page Tables) and AMD's **NPT** (Nested Page Tables) add a second level of address translation in hardware:

```
Guest virtual address
       |
       | (guest page table walk, done in hardware)
       v
Guest physical address
       |
       | (EPT/NPT walk, done in hardware)
       v
Machine physical address
```

No VMEXITs on normal page table access. A TLB miss now requires walking two levels of page tables, but the hardware does it automatically.

## Containers vs. Virtual Machines

Containers (Docker, Kubernetes pods) are a lighter-weight isolation mechanism built on Linux kernel features, not a full hardware abstraction:

```
VMs                              Containers
──────────────────────────────   ──────────────────────────────
App A   App B   App C            App A   App B   App C
Guest   Guest   Guest            Container Container Container
OS A    OS B    OS C             Shared Linux kernel
Hypervisor                       Container runtime (Docker)
Physical Hardware                Physical Hardware
```

### Linux Namespaces

Each container gets its own **namespace** — an isolated view of a global kernel resource:

| Namespace | Isolates |
|-----------|----------|
| `pid` | Process IDs (container has its own PID 1) |
| `net` | Network interfaces, IP addresses, routing tables |
| `mnt` | Mount points (container sees its own filesystem) |
| `uts` | Hostname and domain name |
| `ipc` | System V IPC, POSIX message queues |
| `user` | User and group IDs |

### Control Groups (cgroups)

**cgroups** limit, account for, and isolate resource usage (CPU, memory, disk I/O, network) per group of processes:

```bash
# Limit a container to 2 CPU cores and 512 MB RAM:
cgcreate -g cpu,memory:/mycontainer
cgset -r cpu.cfs_quota_us=200000 mycontainer   # 200ms out of 100ms period = 2 cores
cgset -r memory.limit_in_bytes=536870912 mycontainer
```

### VM vs. Container Trade-offs

| | Virtual Machines | Containers |
|--|-----------------|-----------|
| Isolation level | Strong (hardware boundary) | Weaker (kernel boundary) |
| Startup time | 30–120 seconds | < 1 second |
| Memory overhead | 100s of MB (full OS) | MBs (just the app + libs) |
| Security | Guest kernel exploits don't escape | Kernel vulnerability affects all containers |
| Use case | Multi-tenant cloud, different OSes | Microservices, CI/CD pipelines |

## Para-Virtualization

Rather than trapping and emulating all privileged instructions, **para-virtualization** modifies the guest OS to replace sensitive operations with explicit **hypercalls** to the hypervisor — a cooperative approach:

```c
// Instead of:  wrmsr(MSR_FS_BASE, addr);   // traps, slow
// Guest calls: HYPERVISOR_set_segment_base(SEGBASE_FS, addr);  // explicit, fast
```

**Xen** pioneered para-virtualization. The guest OS must be modified (ported), so unmodified Windows cannot run in para-virtual mode. However, Linux, NetBSD, and FreeBSD all have Xen-aware kernels. Performance approaches native hardware.

## Key Takeaways

- **Type 1 hypervisors** (ESXi, Hyper-V) run directly on hardware; **Type 2** (VirtualBox) run atop a host OS.
- Classic x86 was not cleanly virtualizable; **Intel VT-x / AMD-V** added hardware-assisted virtualization.
- **EPT/NPT** eliminates shadow page table VMEXITs by adding a second hardware page table walk.
- **Containers** use Linux namespaces and cgroups — same kernel, isolated views. Faster and lighter than VMs but with weaker isolation.
- **Para-virtualization** replaces trap-and-emulate with explicit hypercalls for near-native performance at the cost of requiring modified guest OSes.

## Further Reading

- OSTEP Chapter 32 (appendix) — Virtual Machines: https://pages.cs.wisc.edu/~remzi/OSTEP/
- MIT 6.828 Lecture Notes on Virtualization: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/
