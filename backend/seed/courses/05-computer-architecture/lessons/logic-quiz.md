# Quiz: Digital Logic

Test your understanding of logic gates, Boolean algebra, and sequential circuits.

**Q1. What is the output of the expression `(A AND B) OR (NOT A AND C)` when A=1, B=0, C=1?**
- [ ] 1
- [x] 0
- [ ] Depends on previous state
- [ ] Undefined

**Q2. What makes NAND a "universal gate"?**
- [ ] It is faster than all other gates.
- [ ] It uses the fewest transistors in CMOS.
- [x] Any Boolean function can be implemented using only NAND gates.
- [ ] It is the only gate that accepts two inputs.

**Q3. A D flip-flop captures its input D at:**
- [ ] Any time D changes while Enable is HIGH.
- [ ] While the clock is HIGH (level-sensitive).
- [x] The rising (or falling) edge of the clock signal only.
- [ ] When the enable signal goes LOW.

**Q4. De Morgan's theorem states that `NOT(A AND B)` equals:**
- [ ] `(NOT A) AND (NOT B)`
- [x] `(NOT A) OR (NOT B)`
- [ ] `A OR B`
- [ ] `NOT A AND B`

**Q5. A gated D latch differs from an edge-triggered D flip-flop in that:**
- [ ] The D latch uses fewer transistors per bit.
- [x] The D latch is transparent (Q follows D) whenever Enable is HIGH, while the DFF captures D only at the clock edge.
- [ ] The D latch requires a clock signal.
- [ ] The DFF has a forbidden state; the D latch does not.

**Q6. Setup time violation in a synchronous circuit causes:**
- [ ] The circuit to run slower but produce correct results.
- [ ] The clock to stop oscillating.
- [x] Metastable or incorrect output because D was not stable before the clock edge captured it.
- [ ] The flip-flop to reset to 0 on the next cycle.
