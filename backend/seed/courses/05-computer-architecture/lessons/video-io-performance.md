# Video: I/O Systems and Performance Analysis

This video covers how I/O devices connect to the CPU through buses and interrupts, then pivots to the quantitative side of computer architecture: performance metrics, Amdahl's Law, and the implications for parallel system design.

**Key topics covered:**
- Bus architecture: synchronous vs asynchronous buses, address/data/control lines
- Interrupt-driven I/O vs polling vs DMA (Direct Memory Access) for high-bandwidth devices
- Performance metrics: CPU time, clock cycles, CPI, MIPS, and why MIPS is misleading
- Amdahl's Law: the parallelizable fraction limits overall speedup, with worked examples
- Gustafson's Law and scaled workloads in parallel computing
- Real-world DMA and PCIe throughput numbers

**Takeaway:** You will understand how DMA frees the CPU from I/O overhead, be able to apply Amdahl's Law to predict the maximum speedup from any optimization, and know why the non-parallelizable fraction is the dominant bottleneck in parallel systems.
