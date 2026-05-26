# Quiz: Data and Number Representation

**Q1. In 8-bit two's complement, what is the decimal value of the bit pattern `10000000`?**
- [ ] 128
- [x] -128
- [ ] -127
- [ ] 0

**Q2. To negate a two's complement number, you:**
- [ ] Set the MSB to 1 and leave other bits unchanged.
- [ ] Reverse the byte order.
- [x] Flip all bits and add 1.
- [ ] Subtract from 2^N.

**Q3. In 8-bit two's complement, compute `01111111 + 00000001`. The result is:**
- [ ] 10000000 and no overflow flag
- [x] 10000000 and the overflow flag is set (positive + positive = negative)
- [ ] 00000000 with a carry flag
- [ ] 11111111 with undefined behavior

**Q4. In IEEE 754 single precision, the exponent field for the number 1.0 contains:**
- [ ] 0 (all zeros)
- [ ] 128
- [x] 127 (the bias value, representing an exponent of 0)
- [ ] 1

**Q5. Why can't 0.1 be represented exactly in IEEE 754 binary floating-point?**
- [ ] 0.1 is too small for the 8-bit exponent range.
- [x] 0.1 in base 2 is a non-terminating repeating binary fraction (like 1/3 in base 10).
- [ ] The sign bit conflicts with the exponent encoding.
- [ ] It would require a 128-bit format.

**Q6. Sign-extending the 8-bit signed value `11110110` (-10) to 16 bits gives:**
- [ ] `0000000011110110`
- [x] `1111111111110110`
- [ ] `1000000011110110`
- [ ] `0111111111110110`
