# I/O, Buses, and Interrupts

A CPU alone cannot do useful work without communicating with the outside world. This lesson covers how input/output devices connect to the processor and how the CPU handles them efficiently.

## The Bus

A **bus** is a shared communication channel — a set of wires carrying signals between components. A classical bus has three sub-buses:

```
Address bus  — CPU → devices: which location to read/write
Data bus     — bidirectional: the data itself
Control bus  — read/write select, clock, interrupt lines
```

### Bus Trade-offs

| Property | Narrow, Slow Bus | Wide, Fast Bus |
|---|---|---|
| Cost | Low | High |
| Bandwidth | Low | High |
| Wiring | Simple | Complex |

Modern computers use a **hierarchical bus structure**: high-speed PCIe for GPU/NVMe, USB for peripherals, I2C/SPI for low-speed sensors.

## Polling vs Interrupts

The CPU must know when a device has data ready or has finished an operation. Two mechanisms:

### Polling (Busy-Wait)

The CPU repeatedly checks a status register of the device in a loop:

```python
while device.status != READY:
    pass   # spin
data = device.read()
```

Simple to program, but wastes CPU cycles when the device is slow (keyboard, disk). Fine for very fast devices (network card at 100 Gbps) where the wait is brief.

### Interrupts

The device signals the CPU by asserting an **interrupt line**. The CPU:

1. Finishes the current instruction.
2. Saves the PC and registers (pushes context to stack).
3. Jumps to the **Interrupt Service Routine (ISR)** — a registered handler function.
4. Executes the ISR (reads data, acknowledges the device).
5. Restores context and resumes the interrupted program.

```
Normal execution:   A → B → C → [interrupt!] → ISR → D → E
```

Interrupts allow the CPU to do useful work while waiting for slow I/O.

### DMA (Direct Memory Access)

For high-bandwidth I/O (disk, network), having the CPU copy every byte wastes cycles. A **DMA controller** transfers data directly between device and memory, then interrupts the CPU only once when the transfer is complete.

```
CPU initiates DMA:   tell DMA controller: src=disk, dst=memory[0x1000], len=4096
DMA transfers data:  CPU is free to run other code
DMA interrupts CPU:  "transfer complete"
```

## Measuring Performance

### Latency vs Throughput

- **Latency**: time for one operation (e.g., time for one disk read = 5 ms).
- **Throughput**: operations (or bytes) per unit time (e.g., disk bandwidth = 500 MB/s).

These can be independently measured and often trade off against each other.

### CPU Time

```
CPU time = Instruction count × CPI × Clock period
         = Instruction count × CPI / Clock frequency
```

To improve performance, reduce any of the three factors:
- Fewer instructions (better algorithm, better compiler).
- Lower CPI (deeper pipeline, out-of-order execution, forwarding).
- Higher clock frequency (better process technology, smaller gates).

### Benchmark and Workload

Real-world performance is measured with **benchmarks** (SPEC CPU, MLPerf, etc.) that represent typical workloads. Microbenchmarks measure one factor in isolation (memory bandwidth, FP throughput).

## Amdahl's Law

**Amdahl's Law** quantifies the speedup achievable by optimizing one part of a system:

```
Speedup_overall = 1 / ((1 - f) + f / S)

where:
  f = fraction of execution time affected by the improvement
  S = speedup of the improved part
```

### Example

A program spends 40% of its time in a loop. You make the loop 10× faster:

```
Speedup = 1 / (0.6 + 0.4/10) = 1 / (0.6 + 0.04) = 1 / 0.64 ≈ 1.56×
```

Even infinite speedup of that loop gives at most 1/0.6 ≈ 1.67× overall — the **serial bottleneck** limits improvement.

### Implications

- Profile before optimizing: only the hottest path matters.
- Parallelism (more cores) helps mainly if the parallel fraction is large.
- I/O bottlenecks can nullify CPU improvements entirely.
