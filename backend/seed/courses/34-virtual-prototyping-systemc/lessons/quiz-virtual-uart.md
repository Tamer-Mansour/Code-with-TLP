# Quiz: Modeling a Virtual UART and I/O

**Q1. In a 16550-compatible UART, which register must be written to enable access to the baud-rate divisor registers DLL and DLM?**
- [ ] FCR (FIFO Control Register)
- [ ] IER (Interrupt Enable Register)
- [x] LCR (Line Control Register, bit 7 = DLAB)
- [ ] MCR (Modem Control Register)

The Divisor Latch Access Bit (DLAB) is bit 7 of LCR. Setting it to 1 makes offset 0 decode as DLL and offset 1 as DLM, instead of THR/RHR and IER.

---

**Q2. What is the correct initial value of LSR bits 5 and 6 (THRE and TEMT) when the virtual UART model powers on?**
- [ ] Both 0 — the TX FIFO is assumed to be busy at power-on
- [x] Both 1 — the TX FIFO and shift register are both empty at power-on
- [ ] Bit 5 = 1, bit 6 = 0 — holding register empty but shift register still busy
- [ ] Implementation-defined; drivers must not rely on these bits at power-on

Real 16550 hardware powers on with both THRE and TEMT set because there is no data in transit. Drivers that check LSR before the first write rely on this initial state; failing to set it causes an infinite wait.

---

**Q3. A UART driver enables the THREI (Transmitter Holding Register Empty) interrupt before writing the first byte to THR. What happens?**
- [ ] Nothing — THREI only fires after at least one byte has been sent
- [ ] A framing error is reported in LSR
- [x] The THREI interrupt fires immediately because the TX FIFO starts empty
- [ ] The UART resets automatically to prevent the spurious interrupt

THREI is a level-sensitive interrupt that asserts whenever the TX FIFO is empty and THREI is enabled. Since the FIFO is empty at power-on, enabling THREI immediately triggers the interrupt. Correct driver code enables THREI only after writing the first byte.

---

**Q4. A virtual UART model uses a single `std::queue<uint8_t>` for both TX and RX. What is the most likely failure mode?**
- [ ] The model compiles but TX throughput is halved
- [ ] The baud-rate divisor calculation is incorrect
- [x] Concurrent TX writes and RX pushes corrupt each other's data
- [ ] Interrupts are generated twice for every byte

TX and RX FIFOs are independent hardware structures. Sharing one queue means a TX enqueue can appear in the RX path and vice versa, leading to data corruption under any overlapping traffic.

---

**Q5. Which of the following correctly describes how the IIR (Interrupt Identification Register) signals "no interrupt pending"?**
- [x] Bit 0 of IIR is 1 when no interrupt is pending
- [ ] IIR reads 0x00 when no interrupt is pending
- [ ] IIR reads 0xFF when no interrupt is pending
- [ ] Bit 7 of IIR is set when no interrupt is pending

In the 16550 convention, IIR bit 0 is the "Interrupt Pending" flag — but it is **active-low**: 0 means an interrupt IS pending, 1 means no interrupt is pending. This inverted logic is a classic source of bugs when implementing or reading the IIR handler.

---

**Q6. When connecting a virtual UART to the host console, why must the terminal be set to raw mode?**
- [ ] Raw mode increases the baud rate of the host serial port
- [ ] Raw mode is required for PTY backends but not for stdin/stdout
- [ ] Raw mode disables the kernel's TCP buffering for socket backends
- [x] Raw mode disables line-buffering and local echo so input is delivered character-at-a-time

By default, POSIX terminals buffer input until Enter is pressed (canonical mode) and echo characters locally. Embedded firmware expects character-at-a-time delivery with no echo. Setting `ICANON=0` and `ECHO=0` (raw mode) gives the model the same character stream the real hardware would receive.
