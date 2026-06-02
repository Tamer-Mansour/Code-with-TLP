# Modeling a Virtual DMA Engine

A Direct Memory Access (DMA) engine transfers data between memory regions or between peripherals and memory **without CPU involvement**. In a virtual prototype, a DMA model is essential for accurate performance modeling and for running software that relies on DMA for high-throughput I/O (network, storage, audio).

## What a DMA Engine Does

1. **Software programs the DMA:** Sets source address, destination address, byte count, and issues a start command via MMIO.
2. **DMA reads from source:** Issues bus transactions (TLM reads) to the source address.
3. **DMA writes to destination:** Issues bus transactions (TLM writes) to the destination address.
4. **Transfer completes:** DMA asserts an IRQ and sets a status flag.

The CPU is free to do other work during the transfer — this is the fundamental benefit of DMA.

## Register Map (Simple DMA)

| Offset | Register | Description |
|---|---|---|
| 0x00 | SRC_ADDR | Source start address |
| 0x04 | DST_ADDR | Destination start address |
| 0x08 | LENGTH | Number of bytes to transfer |
| 0x0C | CTRL | Bit 0: Start; Bit 1: IRQ enable |
| 0x10 | STATUS | Bit 0: Busy; Bit 1: Done (W1C) |

## SystemC DMA Model

```cpp
SC_MODULE(DMA) {
    // MMIO interface (CPU programs the DMA)
    tlm_utils::simple_target_socket<DMA> ctrl_socket;

    // Bus master interface (DMA reads/writes memory)
    tlm_utils::simple_initiator_socket<DMA> bus_socket;

    // Interrupt output
    sc_out<bool> irq;

    uint32_t src_addr, dst_addr, length, ctrl, status;
    sc_event  start_event;

    void dma_thread() {
        while (true) {
            wait(start_event);          // wait for SW to write CTRL.Start
            status |= STATUS_BUSY;
            status &= ~STATUS_DONE;

            uint8_t buf[4];
            for (uint32_t offset = 0; offset < length; offset += 4) {
                uint32_t chunk = std::min(4u, length - offset);

                // Read from source
                tlm::tlm_generic_payload rd;
                sc_time delay = SC_ZERO_TIME;
                rd.set_read();
                rd.set_address(src_addr + offset);
                rd.set_data_ptr(buf);
                rd.set_data_length(chunk);
                bus_socket->b_transport(rd, delay);
                wait(delay);

                // Write to destination
                tlm::tlm_generic_payload wr;
                wr.set_write();
                wr.set_address(dst_addr + offset);
                wr.set_data_ptr(buf);
                wr.set_data_length(chunk);
                bus_socket->b_transport(wr, delay);
                wait(delay);
            }

            status &= ~STATUS_BUSY;
            status |= STATUS_DONE;
            if (ctrl & CTRL_IRQ_EN) {
                irq.write(true);
                wait(SC_ZERO_TIME);
                irq.write(false);
            }
        }
    }

    SC_CTOR(DMA) : ctrl_socket("ctrl"), bus_socket("bus") {
        SC_THREAD(dma_thread);
        ctrl_socket.register_b_transport(this, &DMA::b_transport);
    }
};
```

## Two-Socket Architecture

The DMA has **two TLM sockets**, which is a key design point:

- **Target socket (`ctrl_socket`):** CPU writes configuration registers here.
- **Initiator socket (`bus_socket`):** DMA uses this to access memory on behalf of transfers.

This correctly models the fact that a real DMA is a bus master — it initiates transactions, it does not just respond to them.

## Timing Accuracy

| Approach | How to Model |
|---|---|
| Approximate (functional) | `wait(SC_ZERO_TIME)` per beat — fast simulation |
| Cycle-accurate | `wait(N * clk_period)` per beat — slower but precise |
| Annotated | Use TLM DMI and annotate bus latency |

For software development, approximate timing is usually sufficient. For performance analysis, annotate each beat with realistic bus latency.

## Scatter-Gather DMA

Advanced DMA controllers support scatter-gather: a linked list of descriptor structs, each containing src, dst, length. The DMA model reads descriptors from memory (via `bus_socket`) and chains them automatically:

```cpp
struct DMADescriptor {
    uint32_t src;
    uint32_t dst;
    uint32_t len;
    uint32_t next;  // 0 = end of chain
};
```

## Common Pitfalls

- **Forgetting the initiator socket:** Modelers sometimes use only a target socket and try to pass data via shared memory — this bypasses the bus model and breaks memory-mapped I/O correctness.
- **No delay on transfers:** Without any `wait()`, all bytes transfer in zero simulation time — the CPU model never observes the DMA as busy.
- **W1C on STATUS.Done:** Software must write 1 to clear the Done bit; if not modeled, the interrupt handler sees Done=1 forever.
- **DMA and CPU both accessing the same buffer:** Without proper cache-coherency modeling, the CPU may read stale data after the DMA completes.

> **Interview answer:** A virtual DMA model has two TLM sockets — a target socket for CPU configuration and an initiator socket for bus-mastered memory transfers. An `SC_THREAD` waits for a start event, then issues a series of TLM reads and writes through the bus socket with annotated delays, and asserts an IRQ when the transfer completes.
