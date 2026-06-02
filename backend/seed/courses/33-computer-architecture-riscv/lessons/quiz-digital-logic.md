# Quiz: Digital Logic and Boolean Algebra

**Q1. Which gate is individually "functionally complete" — meaning any Boolean function can be built using only that one gate type?**
- [ ] AND
- [ ] OR
- [x] NAND
- [ ] XOR

AND and OR together are not individually complete. XOR cannot produce a constant 0 or 1 alone. NAND (and NOR) are each individually functionally complete.

---

**Q2. Applying De Morgan's theorem to `¬(A · B)` gives:**
- [ ] `Ā · B̄`
- [x] `Ā + B̄`
- [ ] `A + B`
- [ ] `A · B`

De Morgan: negate a product by breaking the bar and changing AND to OR. `¬(A · B) = Ā + B̄`.

---

**Q3. In a 4-variable Karnaugh map, what is the maximum number of cells a single valid group can contain?**
- [ ] 4
- [ ] 8
- [x] 16
- [ ] 12

A 4-variable K-map has 16 cells total. A group of all 16 ones simplifies to the constant 1. Groups must be powers of 2; 12 is not a power of 2.

---

**Q4. What distinguishes a D flip-flop from a D latch?**
- [ ] A flip-flop uses NAND gates; a latch uses NOR gates
- [ ] A flip-flop has more storage capacity
- [x] A flip-flop is edge-triggered; a latch is level-sensitive
- [ ] A latch requires a clock; a flip-flop does not

The critical difference: a latch is transparent while its enable is high (level-sensitive). A flip-flop samples only at the clock edge (edge-triggered), making synchronous timing analysis straightforward.

---

**Q5. In a Moore FSM, the outputs depend on:**
- [ ] Current inputs only
- [x] Current state only
- [ ] Current state and current inputs
- [ ] Next state and current inputs

Moore outputs are a function of state only. Mealy outputs depend on both state and inputs. Moore outputs are glitch-free because they only change at clock edges (when state changes).

---

**Q6. The Boolean expression `A + A·B` simplifies to:**
- [ ] `A·B`
- [ ] `B`
- [x] `A`
- [ ] `A + B`

This is the Absorption law: `A + A·B = A`. The term `A·B` is fully "absorbed" into `A` because whenever `A·B = 1`, `A` must already be 1.
