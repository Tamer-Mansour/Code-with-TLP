# Bringing Up a UART Driver Against the Model

Getting a real firmware UART driver to run correctly against a virtual model is the true test of the model's fidelity. This lesson walks through the bringup sequence, common failure modes, and how to use the virtual platform to debug driver issues that would be difficult to catch on real hardware.

## The Bringup Sequence

A typical embedded UART driver initialization follows this sequence:

```c
/* 1. Set baud rate: divisor = clock / (16 * baud) */
uint16_t div = UART_CLK / (16 * 115200);
uart_write(LCR, 0x80);          /* DLAB=1 */
uart_write(DLL, div & 0xFF);
uart_write(DLM, (div >> 8) & 0xFF);

/* 2. Set 8N1: 8-bit word, no parity, 1 stop bit */
uart_write(LCR, 0x03);          /* DLAB=0, 8N1 */

/* 3. Enable and reset FIFOs, trigger level = 14 */
uart_write(FCR, 0xC7);

/* 4. Enable DTR and RTS */
uart_write(MCR, 0x03);

/* 5. Enable RX and TX interrupts */
uart_write(IER, 0x03);
```

The virtual model must handle every one of these writes without faulting. In particular, the DLAB sequence at step 1 is a common failure point: if the model does not implement DLAB, writes to DLL/DLM will corrupt THR, and the driver will send garbage on the first transmit.

## Verifying the Model Against a Known Driver

Use a simple polled transmit function as the first test:

```c
void uart_putc(char c) {
    while (!(uart_read(LSR) & 0x20));  /* wait for THRE */
    uart_write(THR, c);
}

void uart_puts(const char *s) {
    while (*s) uart_putc(*s++);
}
```

If `uart_puts("Hello\r\n")` appears on the host console, the TX path, the LSR THRE bit, and the THR write are all working.

## Debugging with a Trace Log

Add a trace log to the model's `b_transport` handler. Printing every register access makes it easy to spot mismatches:

```cpp
void UartModel::b_transport(tlm::tlm_generic_payload &trans, sc_core::sc_time &delay) {
    uint8_t reg  = trans.get_address() & 0x7;
    bool    is_wr = (trans.get_command() == tlm::TLM_WRITE_COMMAND);
    uint8_t *data = reinterpret_cast<uint8_t *>(trans.get_data_ptr());

    if (trace_) {
        printf("[UART] %s reg=%u val=0x%02X @ %s\n",
               is_wr ? "WR" : "RD", reg,
               is_wr ? *data : 0,
               sc_core::sc_time_stamp().to_string().c_str());
    }
    // ... normal handling
}
```

Compare the trace against a known-good hardware capture (e.g., from a logic analyzer) to find divergences.

## Interrupt-Driven Bringup

After polled TX works, test interrupt-driven operation:

```c
void uart_isr(void) {
    uint8_t iir = uart_read(IIR);
    if (iir & 0x01) return;          /* no interrupt pending */

    switch (iir & 0x0E) {
    case 0x04:                        /* RX data available */
        rx_buf[rx_head++] = uart_read(RHR);
        break;
    case 0x02:                        /* TX holding register empty */
        if (tx_head < tx_tail)
            uart_write(THR, tx_buf[tx_head++]);
        else
            uart_write(IER, uart_read(IER) & ~0x02); /* disable THREI */
        break;
    }
}
```

Common failures at this stage:

| Symptom | Likely Cause |
|---|---|
| ISR never called | IRQ line not connected to interrupt controller model |
| ISR called once, then stops | THREI not re-enabled after TX buffer refill |
| ISR called infinitely | IRQ not deasserted (level-sensitive, cause not cleared) |
| Garbled RX data | RX FIFO pop does not update DR bit in LSR |

## Using the Model to Test Edge Cases

Virtual platforms excel at reproducing hardware edge cases:

- **Inject framing errors** — set LSR bit 3 and assert the RLSI interrupt to test the driver's error recovery path.
- **Simulate FIFO overflow** — push bytes into the RX FIFO faster than the driver reads them; verify the OE bit and OE interrupt handler.
- **Test baud-rate change at runtime** — write new DLL/DLM values mid-transfer; confirm the driver handles the transition correctly.

These scenarios are impossible or risky to reproduce on physical hardware during development.

## Running a Linux UART Driver Against the Model

If the virtual platform models a full SoC (CPU + memory + interrupt controller + UART), you can boot Linux and observe the 8250 driver initializing against your model. The dmesg output should show:

```
Serial: 8250/16550 driver, 1 ports, IRQ sharing disabled
00000000.uart: ttyS0 at MMIO 0x10000000 (irq = 33) is a 16550A
```

If instead you see `... is an unknown serial port` the model's scratch register (SCR) latch is broken — Linux uses it for detection.

**Interview answer:** Bring up a UART driver against the virtual model by first testing polled TX (checking LSR THRE before writing THR), then enabling interrupts and verifying the ISR fires and deasserts correctly. Use register-access tracing to compare against hardware captures, and inject error conditions (OE, FE) to test driver error paths.

## Common Pitfalls

- **Wrong base address in the device tree** — the Linux driver will not probe if the UART base address in the DTS does not match the model's TLM socket address.
- **Missing SCR latch** — the 8250 Linux driver writes a byte to SCR and reads it back; if SCR is not a plain latch the driver falls back to a dumber serial port type.
- **Interrupt controller not connected** — the IRQ line from the UART must be wired to the interrupt controller model; leaving it unconnected means interrupts fire in the UART model but the CPU never sees them.
