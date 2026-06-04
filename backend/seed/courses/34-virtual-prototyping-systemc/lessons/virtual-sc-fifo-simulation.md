# SC_FIFO Bounded Queue Simulation

`sc_fifo` is one of SystemC's most useful primitive channels. It models a bounded FIFO queue with blocking read and write semantics, which directly maps to real hardware patterns like UART transmit/receive buffers, DMA descriptor rings, and inter-process communication queues.

## What sc_fifo Provides

The `sc_fifo<T>` template channel implements two interfaces:

- `sc_fifo_in_if<T>`: the read side — `read()`, `nb_read()`, `num_available()`, `data_written_event()`
- `sc_fifo_out_if<T>`: the write side — `write()`, `nb_write()`, `num_free()`, `data_read_event()`

```cpp
sc_fifo<uint8_t> tx_fifo(16);  // 16-element FIFO

// Producer (SC_THREAD)
void producer() {
    while (true) {
        tx_fifo.write(next_byte());  // blocks if full
    }
}

// Consumer (SC_THREAD)
void consumer() {
    while (true) {
        uint8_t b = tx_fifo.read();  // blocks if empty
    }
}
```

## Blocking vs Non-Blocking

Both blocking and non-blocking variants exist:

| Method | Behavior when blocked |
|--------|----------------------|
| `write(val)` | Suspends SC_THREAD until space is available |
| `nb_write(val)` | Returns `false` immediately if full |
| `read()` | Suspends SC_THREAD until data is available |
| `nb_read(val)` | Returns `false` immediately if empty |

Only `SC_THREAD` processes can use the blocking forms because they call `wait()` internally. `SC_METHOD` processes must use `nb_read` / `nb_write`.

## Simulation Semantics

When a producer calls `write()` on a full FIFO, the process suspends and the kernel schedules the next ready process. When the consumer reads from the FIFO, the `data_read_event` fires, which wakes the blocked producer at the next delta cycle.

This interleaving means that at any given simulation timestamp, you may see the producer blocked while the consumer drains entries, or the consumer blocked while the producer fills entries. The observable behavior depends on the current FIFO occupancy.

## Common Use Cases

**UART TX modeling**: software writes bytes into the TX FIFO; the UART peripheral model reads them one at a time at the configured baud rate.

**DMA staging buffer**: a DMA engine fills a FIFO from memory; the peripheral drains it at the device rate. If the DMA is faster than the device, the FIFO fills and the DMA blocks — exactly as it would in hardware.

**Inter-module data flow**: when two modules need to exchange a stream of items without tight coupling, `sc_fifo` provides a clean interface that hides whether the producer and consumer run at the same rate.

## Capacity Choice

The capacity you give to `sc_fifo` models the hardware buffer depth. Setting it to 1 simulates a register-based single-entry buffer; larger values model deeper hardware FIFOs. Setting it too large relative to the real hardware will hide stall conditions that the real system would experience.

## Alternative: sc_fifo vs Custom Channels

`sc_fifo` is a primitive channel built into the SystemC library. For more complex queuing behavior — priority ordering, peek-without-dequeue, or per-element timestamps — you must implement a hierarchical channel (a module that itself implements an interface). `sc_fifo` handles the simple but common case well enough that most SystemC models use it directly.

## Reference

For the complete `sc_fifo` API:

- **IEEE Std. 1666-2023** (free via Accellera at https://www.accellera.org/downloads/standards/systemc): Section 8.4 specifies the full `sc_fifo` interface including event semantics and reference counting
- **SystemC and TLM-2.0 Introductory Tutorial** (Doulos, free PDF at https://www.doulos.com/media/1408/systemc_tutorial.pdf): Shows `sc_fifo` in the context of producer-consumer channel examples

> **Interview answer:** `sc_fifo<T>` is a SystemC primitive channel implementing a bounded blocking queue. It provides `write()` (blocks if full) and `read()` (blocks if empty) for SC_THREAD processes, and non-blocking `nb_write` / `nb_read` for SC_METHOD processes. It is used to model hardware FIFOs like UART buffers and DMA staging queues.
