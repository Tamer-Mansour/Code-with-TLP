# Nested Paging (EPT) and the IOMMU

CPU virtualization handles instructions, but memory and I/O device access require their own virtualization layers. **Extended Page Tables (EPT)** and the **IOMMU** are the two hardware mechanisms that close these gaps.

## The Memory Virtualization Problem

A guest OS manages its own virtual-to-physical address mappings using page tables. But the "physical" addresses the guest writes into its page tables are **guest physical addresses (GPA)** — they are not real hardware addresses. The real hardware addresses are **host physical addresses (HPA)**.

Without hardware help, the VMM must maintain **shadow page tables** that compose both mappings:

```
Guest Virtual → (guest page table) → Guest Physical
                                         │
                              (VMM shadow table)
                                         │
                                    Host Physical
```

Every guest page table write causes a VM Exit so the VMM can update the shadow table. This is **very expensive** for workloads that modify page tables frequently (e.g., `fork()` in Linux).

## Extended Page Tables (EPT) — Intel's Solution

EPT (Intel) / Nested Page Tables NPT (AMD) add a **second level of hardware page-table walking** that the CPU performs automatically, with no VMM involvement:

```
Guest Virtual Address
       │
       ▼  (guest CR3 → guest page tables — GPA output)
Guest Physical Address (GPA)
       │
       ▼  (EPT pointer → EPT tables — HPA output)
Host Physical Address (HPA)
       │
       ▼
Physical RAM
```

The CPU's MMU walks **both** table hierarchies in hardware on every TLB miss. The VMM only needs to maintain the EPT tables (GPA → HPA); the guest freely modifies its own page tables without causing VM Exits.

### EPT Page Fault

If a GPA is not mapped in the EPT, the CPU raises an **EPT violation** (a type of VM Exit). The VMM handles it (e.g., allocates a host page frame, maps it in EPT) and resumes the guest. This is analogous to a regular page fault but at the hypervisor layer.

### TLB Cost

Without EPT, shadow page tables are per-process in the guest, causing many TLB flushes. With EPT, TLB entries cache the full GVA→HPA translation. VT-x tags TLB entries with a **VPID** (Virtual Processor ID) so different VMs and VMCS contexts don't pollute each other's TLB.

| Approach | VM Exits for page table updates | TLB flush on context switch |
|---|---|---|
| Shadow page tables | Many (write-protect guest PT) | Full flush |
| EPT/NPT | None for guest PT changes | VPID tags avoid flush |

## The IOMMU

CPUs can be virtualized efficiently, but DMA-capable devices (NIC, GPU, NVMe) access memory using **physical bus addresses**. Without protection, a guest could program a device to DMA into another guest's memory or the VMM itself.

The **IOMMU** (Intel VT-d / AMD-Vi) is a memory management unit on the PCIe bus that applies page-table-style address translation and access control to DMA transactions.

```
Device issues DMA to "physical" address 0x1000_0000
        │
        ▼
  IOMMU looks up device's I/O page table (per device/function)
        │
        ├── Address allowed + mapped → translates to real HPA → RAM access succeeds
        └── Not mapped / wrong permissions → DMA fault → VMM notified
```

### IOMMU Benefits

- **Isolation:** Each VM gets its own IOMMU domain. A compromised guest cannot DMA outside its assigned memory.
- **PCI Passthrough:** The VMM can assign a physical device directly to a guest (VFIO in Linux). Guest drivers talk to real hardware at native speed. IOMMU maps the guest's GPA for DMA so the device works correctly.
- **Security:** Mitigates DMA attacks even outside virtualization (e.g., Thunderbolt DMA attacks on laptops).

```bash
# Enable IOMMU on Linux (Intel)
# In /etc/default/grub:
GRUB_CMDLINE_LINUX="intel_iommu=on iommu=pt"

# Verify
dmesg | grep -i iommu
# DMAR: IOMMU enabled
```

## Worked Example: GPU Passthrough

A gaming VM running Windows needs direct access to an NVIDIA GPU:

1. VMM (QEMU/KVM) configures IOMMU domain for the GPU's PCIe function.
2. IOMMU maps guest GPA range → HPA range where the GPU's BAR registers and memory live.
3. Guest Windows driver writes to GPU registers — DMA goes through IOMMU, translated safely.
4. GPU interrupts are routed to the guest via **posted interrupts** (VT-x interrupt virtualization).
5. Performance is indistinguishable from bare-metal because no emulation occurs.

## Common Pitfall

Forgetting that EPT improves CPU-side memory access latency but **does not protect I/O**. Without IOMMU, a guest with a passed-through device can still corrupt host memory via DMA. Both are required for secure device assignment.

> **Interview answer:** "EPT adds a hardware second-level page table that translates guest physical to host physical addresses without VMM involvement, eliminating shadow page table VM Exits. The IOMMU applies equivalent address translation and access control to device DMA, enabling safe PCI passthrough and preventing DMA-based escapes."
