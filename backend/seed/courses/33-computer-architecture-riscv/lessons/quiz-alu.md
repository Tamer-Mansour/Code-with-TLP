# Quiz: The Arithmetic Logic Unit

Test your understanding of ALU design, adder circuits, flags, and bit manipulation.

---

**Q1. What is the key difference between a half adder and a full adder?**

- [ ] A half adder can handle 16-bit inputs; a full adder handles 32-bit inputs.
- [ ] A half adder uses XOR gates; a full adder uses AND gates.
- [x] A full adder has a carry-in input; a half adder does not.
- [ ] A half adder produces two output bits; a full adder produces only one.

A half adder takes only two inputs (A, B) and cannot accept a carry from a previous stage. A full adder adds three inputs (A, B, Cin), making it chainable across all bit positions in a multi-bit adder.

---

**Q2. How does the ALU perform subtraction A − B without a dedicated subtract circuit?**

- [ ] It shifts B right by one position before feeding it to the adder.
- [ ] It uses a separate subtractor unit that mirrors the adder.
- [ ] It computes A + B and then inverts the result.
- [x] It inverts every bit of B and sets carry-in to 1, computing A + (~B) + 1.

This exploits the two's complement identity: -B = ~B + 1. By inverting B and setting Cin=1, the adder computes the correct two's complement subtraction with no additional hardware.

---

**Q3. In a ripple-carry adder, why does delay grow linearly with bit width?**

- [ ] Each full adder requires progressively more gates for wider inputs.
- [x] Each bit must wait for the carry-out of the previous bit before computing its own carry.
- [ ] The XOR gates used for the sum bits slow down with wider operands.
- [ ] The decoder logic that selects operations grows with bit width.

Carry signals must propagate serially from bit 0 to bit N-1. The total delay is N times the carry delay of a single full adder stage, giving O(N) critical-path depth.

---

**Q4. The Overflow (V) flag is set correctly by which hardware rule?**

- [ ] Overflow = Carry-out of the MSB AND Sign bit of the result.
- [ ] Overflow = (result == 0) AND (carry-in to MSB == 1).
- [x] Overflow = Carry-into-MSB XOR Carry-out-of-MSB.
- [ ] Overflow = Sign bit of A XOR Sign bit of result.

If the carry entering the most-significant bit position differs from the carry leaving it, the sign bit was incorrectly modified — a signed overflow occurred. This XOR of the two carries is the standard hardware overflow detector.

---

**Q5. Which expression efficiently tests whether integer x is a power of two (x > 0)?**

- [ ] `x % 2 == 0`
- [ ] `x & x == 1`
- [ ] `(x >> 1) == 0`
- [x] `x != 0 && (x & (x - 1)) == 0`

Subtracting 1 from a power of two flips the single set bit and sets all lower bits (e.g., 8 = 1000, 7 = 0111). ANDing gives 0. Any non-power-of-two has multiple set bits, so `x & (x-1)` is non-zero.

---

**Q6. What is the primary advantage of a carry-lookahead adder over a ripple-carry adder?**

- [ ] It uses fewer transistors by sharing gates between bit positions.
- [ ] It eliminates the need for XOR gates in the sum computation.
- [x] It computes carries in parallel from the original inputs, reducing delay to O(log N).
- [ ] It avoids the need for a carry-in at each bit position.

Carry-lookahead adders compute all carry signals simultaneously using generate (G = A AND B) and propagate (P = A XOR B) signals derived directly from the inputs. This eliminates serial carry propagation, reducing critical-path depth from O(N) to O(log N).
