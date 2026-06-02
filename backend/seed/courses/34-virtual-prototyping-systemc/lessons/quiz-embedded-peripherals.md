# Quiz: Embedded Peripherals and Interfaces

**Q1. A UART is configured with f_clk = 16 MHz and a baud-rate divisor (BRD) of 8. What is the resulting baud rate?**

- [ ] 9600 baud
- [ ] 57600 baud
- [x] 125000 baud
- [ ] 115200 baud

The formula is `baud = f_clk / (16 * BRD) = 16,000,000 / (16 * 8) = 125,000 baud`. The factor of 16 is the oversampling ratio built into UART receivers.

---

**Q2. On an SPI bus operating in Mode 0 (CPOL=0, CPHA=0), when does the master sample the MISO line?**

- [ ] On the falling edge of SCLK
- [x] On the rising edge of SCLK
- [ ] Whenever MOSI changes
- [ ] When the chip-select (CS) is released

Mode 0 means clock idles low and data is sampled on the leading (rising) edge. CPHA=0 means sample on the first clock edge, which is the rising edge when CPOL=0.

---

**Q3. Which of the following best describes the I2C open-drain bus requirement?**

- [ ] Each device must drive the line to both high and low levels using push-pull outputs.
- [ ] Only the master drives the lines; slaves are purely passive.
- [x] Any device can pull the line low; an external pull-up resistor pulls it high when no device is driving.
- [ ] The bus uses differential signaling to reduce noise.

I2C lines are wired-AND: any device can assert low (pull down), and the pull-up resistor brings the line high when everyone releases it. This enables multi-master arbitration and slave clock stretching.

---

**Q4. A watchdog timer is kicked from inside an interrupt service routine (ISR) that fires every 100 ms. The main application loop deadlocks. What happens?**

- [ ] The watchdog resets the system immediately because the main loop stopped.
- [ ] The watchdog fires after its full timeout because the ISR keeps kicking it.
- [x] The watchdog continues to be serviced by the ISR, masking the deadlock indefinitely.
- [ ] The RTOS scheduler detects the deadlock and skips the watchdog kick.

Kicking the watchdog from an ISR defeats its purpose. The ISR may continue running correctly while the main thread is stuck. The watchdog should be kicked only from the main application loop to prove liveness.

---

**Q5. A 12-bit ADC with V_ref = 3.3 V reads a digital code of 2048. What is the approximate input voltage?**

- [ ] 1.60 V
- [x] 1.65 V
- [ ] 2.20 V
- [ ] 0.80 V

`V_in = code * V_ref / (2^N - 1) = 2048 * 3.3 / 4095 = 1.6498... V ≈ 1.65 V`. The maximum code (4095) maps to V_ref, not to 2^12 = 4096.

---

**Q6. A hardware timer has f_clk = 72 MHz, PSC = 71, and ARR = 999. What is the timer overflow period?**

- [ ] 1 µs
- [ ] 100 µs
- [x] 1 ms
- [ ] 10 ms

`f_timer = 72 MHz / (71 + 1) = 1 MHz` (1 µs per tick). Period `= (ARR + 1) / f_timer = 1000 / 1,000,000 = 1 ms`. The `+1` in both PSC and ARR is the classic off-by-one to remember.
