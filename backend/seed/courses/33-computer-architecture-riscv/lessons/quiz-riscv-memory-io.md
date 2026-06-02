# Quiz: RISC-V Memory System and I/O

Test your understanding of the RISC-V physical memory map, MMIO, PMP, virtual memory schemes, and TLB management.

---

**Q1. Which field of the `satp` CSR selects between Sv39 and Sv48 paging modes?**

- [ ] PPN (Physical Page Number)
- [x] MODE
- [ ] ASID
- [ ] MPRV bit in `mstatus`

_The MODE field (bits 63:60 in RV64) selects the paging scheme: 0=Bare, 8=Sv39, 9=Sv48. PPN points to the root page table; ASID tags TLB entries._

---

**Q2. In Sv39, how many bits does each VPN level index occupy?**

- [ ] 10 bits
- [ ] 12 bits
- [x] 9 bits
- [ ] 8 bits

_Sv39 splits the 39-bit virtual address as VPN[2]:VPN[1]:VPN[0]:offset = 9:9:9:12. Each 9-bit index can address 512 entries in a 4 KiB page (512 × 8 bytes = 4096 bytes)._

---

**Q3. What does a RISC-V PTE with V=1, R=0, W=1, X=0 represent?**

- [ ] A valid read-only leaf page
- [ ] A pointer to the next page table level
- [ ] A huge-page mapping
- [x] A reserved (illegal) encoding that causes a page fault

_The spec forbids W=1 with R=0; this combination is reserved. Hardware must raise a page fault when it encounters it. W=1, R=0, X=0 with V=1 cannot be either a valid leaf or a pointer PTE._

---

**Q4. After modifying a PTE in a shared kernel mapping visible to multiple harts, what additional step is required beyond executing `SFENCE.VMA` on the local hart?**

- [ ] Write back the modified cache line using `CBO.FLUSH`
- [ ] Write 1 to the global TLB-flush MMIO register
- [x] Send an IPI to all other harts sharing the mapping so they each execute `SFENCE.VMA`
- [ ] Set the G (global) bit in the PTE before the flush

_`SFENCE.VMA` only flushes the TLB on the hart that executes it. Other harts retain stale TLB entries. A TLB shootdown — sending an IPI that triggers `SFENCE.VMA` on every sharing hart — is required for correctness._

---

**Q5. Which PMP address-matching mode is most efficient for protecting a naturally aligned power-of-two region?**

- [ ] TOR (Top of Range)
- [ ] NA4 (Naturally Aligned 4-byte)
- [x] NAPOT (Naturally Aligned Power-Of-Two)
- [ ] OFF (disabled)

_NAPOT encodes both the base address and size in a single `pmpaddr` register using a trailing-ones encoding, making it ideal for power-of-two regions. TOR requires two entries (one for the base via the previous entry and one for the top)._

---

**Q6. On a RISC-V system using Sv39, what happens if bits 63:39 of a virtual address are NOT all equal to bit 38?**

- [ ] The hardware ignores the upper bits and translates using only bits 38:0
- [ ] The hardware uses the upper bits as an extended ASID
- [x] The hardware raises a page fault immediately without performing a table walk
- [ ] The hardware switches to Sv48 mode automatically

_Sv39 requires canonical virtual addresses: bits 63:39 must be sign extensions of bit 38. A non-canonical address causes an immediate instruction/load/store page fault before any TLB lookup or table walk is attempted._
