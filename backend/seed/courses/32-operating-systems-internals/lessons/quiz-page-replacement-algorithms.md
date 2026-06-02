# Quiz: Page Replacement Algorithms

**Q1. Which page replacement algorithm always produces the minimum number of page faults for any reference string?**

- [ ] FIFO
- [ ] LRU
- [x] OPT (Optimal)
- [ ] Clock

OPT evicts the page whose next use is farthest in the future, guaranteeing the theoretical minimum. It cannot be implemented in a real OS because it requires knowledge of future references.

---

**Q2. A system uses FIFO with 3 frames on reference string `1 2 3 4 1 2 5 1 2 3 4 5`. Switching to 4 frames produces MORE page faults. This phenomenon is called:**

- [ ] Thrashing
- [ ] Working set violation
- [x] Belady's anomaly
- [ ] Frame starvation

Belady's anomaly is the counterintuitive increase in page faults when more frames are allocated, and it can occur with non-stack algorithms such as FIFO.

---

**Q3. Which of the following is a "stack algorithm" — one that guarantees adding more frames never increases page faults?**

- [ ] FIFO
- [x] LRU
- [ ] Random replacement
- [ ] MFU (Most Frequently Used)

LRU is a stack algorithm: the set of pages held in `n+1` frames is always a superset of those held in `n` frames. OPT also satisfies this property; FIFO and Random do not.

---

**Q4. The clock (second-chance) algorithm decides whether to evict a page based on which hardware-maintained bit?**

- [ ] Dirty bit (modified bit)
- [x] Reference bit (accessed bit)
- [ ] Valid/present bit
- [ ] Protection bit

The clock algorithm uses the reference bit set by the MMU on every page access. A page with ref=1 gets a second chance (bit cleared); a page with ref=0 is evicted. The enhanced clock variant also considers the dirty bit.

---

**Q5. A process has a page fault rate above the upper threshold defined by the Page Fault Frequency (PFF) policy. What action should the OS take?**

- [ ] Suspend the process to reduce load
- [ ] Reduce the number of frames allocated to the process
- [x] Increase the number of frames allocated to the process
- [ ] Switch the process from global to local replacement

PFF is a feedback control mechanism: a fault rate above the upper threshold means the process does not have enough frames, so the OS allocates more. A rate below the lower threshold triggers reclamation.

---

**Q6. With LRU replacement and 3 frames, which page is evicted when a fault occurs and frames contain pages {A, B, C} with last-access order A (oldest) → B → C (most recent)?**

- [x] Page A
- [ ] Page B
- [ ] Page C
- [ ] The page with the highest page number

LRU evicts the page whose most recent access was the longest ago — page A in this case, as it is the least recently used.
