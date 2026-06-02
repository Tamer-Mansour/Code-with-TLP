# Paravirtualization and Virtio

Full virtualization aims to run an **unmodified** guest OS. Paravirtualization takes a different trade-off: modify the guest OS to cooperate with the hypervisor, and gain significant performance in return.

## What Is Paravirtualization?

In paravirtualization, the guest OS is aware it is running in a virtualized environment. Instead of executing sensitive instructions that would cause VM Exits, the guest calls **hypercalls** — a hypervisor API, analogous to system calls from user space to the kernel.

```
Full virtualization:         Paravirtualization:
  Guest → sensitive instr.     Guest → hypercall API
  CPU → VM Exit                Hypervisor handles directly
  VMM → emulate                (fewer mode switches)
  VMM → VMRESUME
```

## Xen's Original Model

Xen (2003) was the pioneering paravirtualization hypervisor. Guest Linux kernels were patched to:

- Replace `HLT` with a `HYPERVISOR_sched_op(SCHEDOP_block)` hypercall.
- Replace `LGDT`/`LIDT` with hypercalls to update descriptor tables.
- Use a **shared memory ring buffer** for I/O instead of emulated device registers.

The result: 2–8× better I/O throughput compared to full emulation at the time, with minimal CPU overhead.

## Hypercall Interface

```c
/* Xen-style hypercall (simplified) */
static inline long hypercall1(unsigned int op, unsigned long arg1)
{
    long ret;
    __asm__ volatile (
        "vmcall"           /* Intel: VMCALL; AMD: VMMCALL */
        : "=a"(ret)
        : "a"(op), "D"(arg1)
        : "memory"
    );
    return ret;
}

/* Guest asking hypervisor to yield the vCPU */
hypercall1(SCHEDOP_yield, 0);
```

## Virtio: The Standard Paravirtual I/O Framework

As hardware VT-x solved CPU virtualization, the remaining performance bottleneck became **I/O** — disk and network. The industry standardized on **virtio** (Virtual I/O), an open specification for paravirtual devices (OASIS standard, used by KVM, Xen, VMware, cloud providers).

### Virtio Architecture

```
Guest OS
  └── virtio driver (frontend)
        │  shared memory ring buffers (virtqueues)
        ▼
  Hypervisor (QEMU/KVM)
  └── virtio backend (vhost-net, vhost-blk, or vhost-user)
        │
        ▼
  Host NIC / Disk
```

The key structure is the **virtqueue** (or vring): a circular buffer in shared memory holding descriptor chains. The guest fills descriptors with I/O request data, kicks the hypervisor via an MMIO write (or `ioeventfd`), and the hypervisor processes requests and signals completion via an interrupt.

### Virtio Devices

| Virtio Device | Replaces |
|---|---|
| `virtio-net` | Emulated e1000 NIC |
| `virtio-blk` | Emulated IDE/SATA disk |
| `virtio-scsi` | Emulated SCSI controller |
| `virtio-balloon` | Memory overcommit management |
| `virtio-gpu` | Display output |
| `virtio-fs` | Host-guest filesystem sharing |

### Performance Comparison

| Device type | Throughput (relative) |
|---|---|
| Fully emulated (e1000) | 1× |
| Virtio-net | 5–10× |
| Virtio-net + vhost (kernel bypass) | 15–30× |
| SR-IOV (hardware passthrough) | ~30× (near native) |

## PVHVM: Best of Both Worlds

Modern deployments use **PVHVM** (Paravirtualized Hardware Virtual Machine): the guest runs in full hardware virtualization mode (VT-x), but uses virtio/paravirtual drivers for I/O. This gives:

- Unmodified kernel compatibility (no full PV patches needed).
- Near-native I/O performance via virtio.
- Full VT-x security isolation.

AWS uses this model (Nitro hypervisor with paravirtual drivers via the Nitro card).

## Common Pitfall

Thinking paravirtualization is obsolete. While full-VM PV (Xen classic) is rare, **virtio is everywhere** — every cloud VM you run on AWS, GCP, or Azure almost certainly uses virtio-net and virtio-blk. Understanding the virtqueue model is practically useful when debugging VM I/O performance.

> **Interview answer:** "Paravirtualization modifies the guest OS to use hypercalls instead of sensitive instructions, reducing VM Exit overhead. Virtio standardizes paravirtual I/O via shared-memory ring buffers (virtqueues), giving 5–30× better throughput than device emulation. Modern VMs combine VT-x for CPU with virtio for I/O."
