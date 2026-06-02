# Hardware Virtualization Support (VT-x/AMD-V)

Intel and AMD both recognized that software-only virtualization was fragile and slow on x86. They independently introduced CPU extensions — **Intel VT-x** (Virtualization Technology for x86) and **AMD-V** (AMD Virtualization, also called SVM — Secure Virtual Machine) — that make x86 fully virtualizable in hardware.

## The Root Problem Solved

Classic x86 trap-and-emulate failed because some sensitive instructions didn't trap. VT-x/AMD-V fix this by introducing a **new CPU execution mode** that is orthogonal to the existing ring hierarchy.

```
Before VT-x:                    After VT-x:
Ring 0 (VMM)                    VMX Root Mode    (VMM, ring 0)
Ring 1 (Guest kernel) ← broken  VMX Non-Root     (Guest, rings 0–3)
Ring 3 (Guest user)
```

In **VMX Non-Root mode**, the guest runs with full ring-0 privileges for its own instructions, but any access to hardware state triggers a **VM Exit** into the VMM automatically, without the fragile ring-compression trick.

## Key VT-x Structures

### VMCS — Virtual Machine Control Structure

The VMCS is a per-VM data structure in memory that the CPU manages with dedicated instructions:

| Field Group | Contents |
|---|---|
| Guest state | RIP, RSP, CR0, CR3, CR4, RFLAGS, segment registers |
| Host state | VMM's register state to restore on VM Exit |
| VM-execution controls | Which events cause a VM Exit (e.g., I/O, CR writes) |
| VM-exit information | Reason for the exit, faulting instruction |
| VM-entry controls | Inject interrupts/exceptions into the guest |

```asm
; VMM sets up VMCS and launches the guest
VMXON  [vmxon_region]   ; enable VMX mode
VMCLEAR [vmcs_ptr]      ; initialize a VMCS
VMPTRLD [vmcs_ptr]      ; make it the current VMCS
VMWRITE field, value    ; configure guest/host state
VMLAUNCH                ; first launch (or VMRESUME for re-entry)
```

### VM Exit and VM Entry

- **VM Exit:** Guest hits a controlled event → CPU atomically saves guest state to VMCS guest area, loads host state from VMCS host area, jumps to VMM's exit handler.
- **VM Entry (VMRESUME):** VMM finishes handling → CPU loads guest state from VMCS, returns to guest execution.

This round-trip costs roughly **1,000–3,000 cycles** on modern hardware, down from ~10,000+ with binary translation.

## AMD-V / SVM Equivalents

AMD's implementation is conceptually identical but uses different terminology and instructions:

| Intel VT-x | AMD-V (SVM) |
|---|---|
| VMCS | VMCB (VM Control Block) |
| VMXON | VMRUN |
| VMLAUNCH/VMRESUME | VMRUN (same instruction) |
| VM Exit | #VMEXIT |
| EPT | NPT (Nested Page Tables) |

## What Causes a VM Exit?

The VMM configures the VMCS to specify exactly which events exit to the hypervisor:

- Writes to control registers (CR0, CR3, CR4)
- Execution of `HLT`, `CPUID`, `RDMSR`, `WRMSR`
- I/O port accesses (`IN`/`OUT` instructions)
- Interrupts and exceptions the VMM wants to intercept
- APIC access, `RDTSC` (if time virtualization is needed)

Events not in the exit bitmap run **at full native speed** — this is why VT-x achieves near-native performance for compute workloads.

## Checking VT-x Support

```bash
# Linux: check CPU flags
grep -m1 vmx /proc/cpuinfo    # Intel
grep -m1 svm /proc/cpuinfo    # AMD

# Also check BIOS — VT-x must be enabled in firmware
```

## Nested Virtualization

Modern VT-x supports **nested virtualization**: running a hypervisor inside a VM (useful for cloud providers offering "bare metal" VMs). The hardware handles the nested VMCS merging so the outer hypervisor doesn't need to fully emulate VT-x instructions.

## Common Pitfall

Assuming VT-x makes ALL virtualization overhead disappear. Memory virtualization still requires **Extended Page Tables (EPT)** for full efficiency — without EPT, every guest page fault causes a VM Exit and shadow page table walk, which is expensive. EPT is covered in the next lesson.

> **Interview answer:** "VT-x/AMD-V add a dedicated guest execution mode (VMX Non-Root / SVM guest) where the guest runs at full ring-0 privileges. A VMCS/VMCB records which events cause a VM Exit back to the hypervisor. This eliminates the need for binary translation and reduces per-trap cost to roughly 1,000–3,000 cycles."
