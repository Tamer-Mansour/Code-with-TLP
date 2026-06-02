# What Is Virtualization?

Virtualization is the technique of running one or more isolated **guest** environments on top of a single physical **host** machine. A software layer called a **hypervisor** (or Virtual Machine Monitor, VMM) sits between the hardware and the guests, presenting each guest with what looks like its own dedicated computer.

## The Core Idea

Without virtualization, an operating system assumes it owns the CPU, memory, and devices entirely. Virtualization breaks that assumption by **multiplexing** the hardware among multiple guests simultaneously, while making each guest believe it has exclusive access.

Three classical requirements for a VMM (Popek & Goldberg, 1974):

| Requirement | Meaning |
|---|---|
| **Fidelity** | Guest software runs identically to running on bare hardware |
| **Safety** | The VMM retains full control of the hardware at all times |
| **Efficiency** | A significant fraction of guest instructions execute directly on the CPU |

## Why Virtualization Matters

- **Server consolidation** — pack many workloads onto one physical server, cutting power and cost.
- **Isolation** — a crash or compromise in one VM does not affect others.
- **Portability** — a VM image can move between physical hosts.
- **Snapshots and live migration** — freeze a running VM state, copy it, resume elsewhere.
- **Testing and development** — run different OSes or kernel versions on one laptop.

## What Gets Virtualized

```
Physical Machine
├── CPU        → vCPUs (virtual CPUs per guest)
├── RAM        → virtual address spaces, balloon drivers
├── Disk       → virtual block devices (qcow2, VMDK, VHD)
├── Network    → virtual NICs, virtual switches (vSwitch)
└── Peripherals → emulated or paravirtual devices
```

Each guest sees a **virtual hardware abstraction**. The VMM intercepts any operation that would affect global state (privileged instructions, I/O, interrupts) and either emulates it, or forwards it safely.

## A Quick Mental Model

Think of the hypervisor as a **strict air-traffic controller**:

- Each airplane (guest OS) believes it owns the sky.
- The controller intercepts every radio call (privileged instruction) and grants or denies clearance.
- Planes never collide because all resource grants go through one authority.

## Key Vocabulary

- **Guest** — the OS running inside the VM.
- **Host** — the physical machine and the OS (if any) running directly on it.
- **VMM / Hypervisor** — the software enforcing isolation.
- **vCPU** — a virtual CPU context scheduled onto a physical core.
- **VM Exit / VM Entry** — transitions between guest mode and hypervisor mode.

## Common Pitfall

Beginners assume virtualization always has high overhead. Modern hardware extensions (Intel VT-x, AMD-V) let most guest instructions run **at native speed**; overhead typically falls to 1–5% for CPU-bound workloads. I/O-heavy workloads see more overhead because device emulation is expensive — paravirtual drivers (virtio) close most of that gap.

> **Interview answer:** "Virtualization uses a hypervisor to abstract physical hardware so multiple isolated guest OSes can share one machine. The VMM intercepts privileged operations, ensuring safety and fidelity while letting most instructions execute natively for efficiency."
