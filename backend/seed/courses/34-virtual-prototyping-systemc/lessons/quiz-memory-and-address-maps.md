# Quiz: Modeling Memory and Address Maps

Test your understanding of memory models, address maps, decoding, and translation in TLM virtual prototypes.

---

**Q1. A TLM router receives a transaction at system address `0x2000_0040`. The SRAM region has base `0x2000_0000` and size `0x2000`. What offset does the router pass to the SRAM target?**

- [ ] 0x2000_0040
- [x] 0x40
- [ ] 0x2000_0000
- [ ] 0x1FC0

The router subtracts the region base from the system address: `0x2000_0040 - 0x2000_0000 = 0x40`. The target only sees the local offset.

---

**Q2. Which response status should a ROM model return when it receives a `TLM_WRITE_COMMAND`?**

- [ ] `TLM_OK_RESPONSE`
- [ ] `TLM_BURST_ERROR_RESPONSE`
- [x] `TLM_COMMAND_ERROR_RESPONSE`
- [ ] `TLM_GENERIC_ERROR_RESPONSE`

A ROM (read-only) region should reject writes with `TLM_COMMAND_ERROR_RESPONSE`, signaling that the command type (write) is not valid for this target.

---

**Q3. You have two address map entries: RegA at `[0x1000_0000, 0x1001_0000)` and RegB at `[0x1000_8000, 0x1001_8000)`. Do they overlap?**

- [x] Yes, they overlap at `[0x1000_8000, 0x1001_0000)`
- [ ] No, RegA ends before RegB starts
- [ ] No, they are adjacent but not overlapping
- [ ] Yes, they overlap for the entire range of RegA

Two intervals `[a, a+sa)` and `[b, b+sb)` overlap if `a < b+sb AND b < a+sa`. Here `0x1000_0000 < 0x1001_8000` and `0x1000_8000 < 0x1001_0000`, so they overlap.

---

**Q4. A sparse memory model receives a read from an address whose page has never been written. What should it return?**

- [ ] A bus error (`TLM_ADDRESS_ERROR_RESPONSE`)
- [x] A default value (typically `0x00`) and `TLM_OK_RESPONSE`
- [ ] The contents of the host OS page at that address
- [ ] `0xDEADBEEF` always

Sparse models return a defined default (zero) for unallocated pages. This models unprogrammed or zeroed memory without allocating host RAM for the entire address range.

---

**Q5. Flash at `0x0800_0000` is mirrored at `0x0000_0000` on a Cortex-M device. A write is issued to `0x0800_0010`. What does a read from `0x0000_0010` return?**

- [ ] Zero, because the mirror is read-only
- [ ] An error, because the mirror address is in the code region
- [x] The same value that was written to `0x0800_0010`
- [ ] Undefined — mirrors are read-only shadows

A mirror points both addresses to the same physical storage. Writing through one address and reading through the mirror address accesses identical bytes. Both router entries forward to the same Flash target with the same offset.

---

**Q6. Which is the correct interval overlap condition for two memory regions A and B?**

- [ ] `A.base == B.base`
- [ ] `A.base + A.size > B.base + B.size`
- [x] `A.base < B.base + B.size AND B.base < A.base + A.size`
- [ ] `A.size == B.size`

This is the standard half-open interval overlap test. Both conditions must hold simultaneously. If either is false, the regions are disjoint.
