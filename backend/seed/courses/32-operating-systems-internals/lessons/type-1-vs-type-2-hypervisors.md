# Type-1 vs Type-2 Hypervisors

Hypervisors come in two broad families that differ in where they sit in the software stack. Knowing the difference — and **why** it matters — is a staple interview question.

## Type-1 Hypervisors (Bare-Metal)

A **Type-1** (or bare-metal) hypervisor runs **directly on the hardware**, with no host OS beneath it. It _is_ the operating system for the physical machine.

```
┌─────────────┬─────────────┐
│   Guest OS  │   Guest OS  │
├─────────────┴─────────────┤
│     Type-1 Hypervisor     │   ← runs on bare hardware
├───────────────────────────┤
│         Hardware          │
└───────────────────────────┘
```

**Examples:** VMware ESXi, Microsoft Hyper-V, Xen, KVM (Linux kernel _is_ the hypervisor).

**Characteristics:**

- Lowest latency — no host OS scheduling layer in between.
- The hypervisor controls hardware drivers directly or via a privileged "dom0" (Xen) or management partition.
- Used in production data centers and cloud infrastructure (AWS, Azure, GCP all use Type-1).
- Smaller attack surface compared to a full host OS.

## Type-2 Hypervisors (Hosted)

A **Type-2** hypervisor runs **as a process inside a host OS**. The host OS manages the hardware; the hypervisor is just another application.

```
┌──────────┬──────────────────┐
│ Guest OS │ Guest OS         │
├──────────┴──────────────────┤
│     Type-2 Hypervisor       │   ← user-space or kernel module
├─────────────────────────────┤
│         Host OS             │
├─────────────────────────────┤
│         Hardware            │
└─────────────────────────────┘
```

**Examples:** VMware Workstation, VirtualBox, QEMU (without KVM), Parallels Desktop.

**Characteristics:**

- Easier to install — no dedicated boot partition needed.
- Shares the host OS scheduler, file system, and drivers.
- Higher overhead: guest I/O request → hypervisor → host OS → driver.
- Ideal for developer desktops, testing, and learning.

## Side-by-Side Comparison

| Property | Type-1 | Type-2 |
|---|---|---|
| Sits on | Bare hardware | Host OS |
| Performance | Near-native | Extra OS layer overhead |
| Primary use | Production servers, cloud | Dev/test, desktop |
| Examples | ESXi, Hyper-V, KVM | VirtualBox, VMware Workstation |
| Attack surface | Smaller | Larger (full host OS exposed) |
| Installation complexity | High | Low |

## The KVM Edge Case

**KVM (Kernel-based Virtual Machine)** is often cited as a Type-1/Type-2 hybrid:

- It is a **kernel module** that turns the Linux kernel itself into a hypervisor.
- The host Linux OS still runs and manages hardware — resembling Type-2.
- But guest VMs interact with hardware via kernel-level code paths, giving Type-1-like performance.
- Most practitioners and the Linux community classify KVM as **Type-1**.

## Why Type-1 Wins in Production

Every extra software layer adds latency and overhead. In a data center running thousands of VMs:

- A Type-2 host OS wastes CPU cycles on its own scheduler, page tables, and drivers.
- Those cycles directly reduce the throughput available to paying customers.
- A Type-1 hypervisor eliminates that waste, improving VM density per host.

## Common Pitfall

Saying "Type-2 is always slower" is an oversimplification. With hardware virtualization (VT-x/AMD-V) and KVM, Type-2-looking setups achieve near-bare-metal CPU performance. The main remaining overhead is **I/O** (disk, network) where the extra host-OS layer still costs latency.

> **Interview answer:** "Type-1 hypervisors run directly on hardware and are used in production for low overhead. Type-2 run atop a host OS, making them easy to install but adding a layer of latency. KVM is a Type-1 variant implemented as a Linux kernel module."
