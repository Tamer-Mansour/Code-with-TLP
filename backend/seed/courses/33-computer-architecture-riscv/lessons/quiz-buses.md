# Quiz: Buses and System Interconnect

**Q1. What is the primary purpose of bus arbitration?**
- [ ] To increase the clock frequency of the bus
- [ ] To decode which device an address belongs to
- [x] To decide which bus master may drive the bus when multiple masters request it simultaneously
- [ ] To convert between synchronous and asynchronous signaling

Arbitration prevents bus fights — electrical conflicts caused by two masters driving the shared lines at the same time. The arbiter grants bus ownership to exactly one master per transaction.

---

**Q2. A system has a 64-bit data bus running at 400 MHz. What is the peak theoretical throughput?**
- [ ] 400 MB/s
- [ ] 1,600 MB/s
- [x] 3,200 MB/s
- [ ] 6,400 MB/s

Peak throughput = (64 bits / 8) × 400 MHz = 8 bytes × 400,000,000 = 3,200,000,000 bytes/s = 3,200 MB/s. Real throughput is lower due to overhead cycles.

---

**Q3. Which of the following correctly describes a synchronous bus?**
- [x] All participants share a common clock, and all signal transitions occur at defined clock edges
- [ ] Devices communicate using a request/acknowledge handshake with no clock
- [ ] Each device has its own independent clock that is negotiated at startup
- [ ] Data is encoded serially with an embedded clock in the data stream

A synchronous bus broadcasts a clock to all devices, which sample and drive signals only at clock edges. Asynchronous buses use the handshake approach described in option B.

---

**Q4. In AXI (AMBA AXI4), why are the read address (AR) and read data (R) channels separate?**
- [ ] To reduce the number of wires needed on chip
- [ ] To support little-endian and big-endian modes simultaneously
- [x] To allow the master to pipeline multiple outstanding transactions by issuing new addresses before receiving previous data
- [ ] To comply with the AMBA bus arbitration protocol

AXI's channel separation enables out-of-order and pipelined operation. The master can send AR requests for transactions 1, 2, 3 back-to-back and receive the read data for each as the slave produces it, hiding latency.

---

**Q5. What is address aliasing, and when does it occur?**
- [ ] When two devices share the same chip-select line and respond to the same address
- [x] When a device responds to multiple address ranges because not all address lines are decoded
- [ ] When the address bus is multiplexed with the data bus to save pins
- [ ] When a cache returns stale data for a memory-mapped I/O register

Partial decoding ignores some address lines, causing the device to appear at several locations in the address map. Full decoding of all address lines prevents aliasing but requires more logic.

---

**Q6. What key architectural change did PCIe make compared to parallel PCI?**
- [ ] PCIe widened the parallel bus from 32 to 128 bits
- [ ] PCIe uses a shared bus with a faster arbiter based on round-robin scheduling
- [ ] PCIe replaced the clock with an asynchronous handshake protocol
- [x] PCIe replaced the shared parallel bus with serial, full-duplex, point-to-point lanes routed through switches

PCIe is fundamentally a switched serial interconnect. Each device gets dedicated lanes (no sharing, no arbitration), and a PCIe switch routes packets by address — eliminating the core limitations of a shared parallel bus.
