# Device Registers and Status/Control Bits

Every peripheral — a UART, a GPIO controller, a SPI bus master, a timer — exposes its state and accepts commands through a small set of hardware registers. Understanding how these registers are structured, and how to read/write them correctly, is the foundation of all device driver programming.

## Register Types

Most peripherals follow a consistent pattern with four broad register categories:

| Register Type | Direction | Purpose |
|---|---|---|
| **Control** | CPU writes | Configure device or issue a command |
| **Status** | CPU reads | Read device state, flags, error conditions |
| **Data** | Both | Transfer payload bytes or words |
| **Configuration / Divisor** | CPU writes at init | One-time setup (baud rate, clock divisor, DMA address) |

Some peripherals combine control and status in a single register (e.g., x86 PIT). Others keep them strictly separate.

## Bit Fields in Registers

Hardware registers pack multiple boolean flags and small fields into one 32-bit (or 8-bit) word. Each bit or group of bits has a specific meaning:

```
SiFive UART txdata register (32-bit)
Bit 31:   full  — 1 = TX FIFO is full; software must not write data
Bits 7:0: data  — the byte to transmit (write only)
```

```
SiFive UART rxdata register (32-bit)
Bit 31:   empty — 1 = RX FIFO is empty; data field is invalid
Bits 7:0: data  — received byte (read only)
```

Always use named bitmask constants instead of raw literals:

```c
#define UART_TXDATA_FULL   (1u << 31)
#define UART_RXDATA_EMPTY  (1u << 31)
#define UART_RXDATA_MASK   0xFFu

// Wait until FIFO has space, then send
void uart_putc(volatile uint32_t *txdata, char c) {
    while (*txdata & UART_TXDATA_FULL)
        ;
    *txdata = (uint32_t)(unsigned char)c;
}

// Read one byte, return -1 if FIFO empty
int uart_getc(volatile uint32_t *rxdata) {
    uint32_t val = *rxdata;
    if (val & UART_RXDATA_EMPTY) return -1;
    return (int)(val & UART_RXDATA_MASK);
}
```

## Read/Write/Clear Semantics

Not all registers behave symmetrically:

- **Read-only (RO)** — Writes are ignored. Status registers are often RO.
- **Write-only (WO)** — Reads return undefined values. Some command registers are WO.
- **Read/Write (R/W)** — Standard bidirectional.
- **Write-1-to-Clear (W1C)** — Writing a `1` to a bit clears it; writing `0` leaves it unchanged. Used for interrupt-pending flags so software can acknowledge individual interrupts without touching others.
- **Read-to-Clear (RC)** — Reading the register clears it automatically. Used by some UART error registers.

```c
// W1C example: clear only the TX-complete interrupt bit (bit 0)
// while leaving all other bits unchanged
#define IRQ_TX_COMPLETE  (1u << 0)
#define IRQ_RX_READY     (1u << 1)

volatile uint32_t *irq_pending = (volatile uint32_t *)0x10013014;

// WRONG: read-modify-write with W1C clears bits you didn't intend to clear
// *irq_pending &= ~IRQ_TX_COMPLETE;   <-- this would write 0 to other bits, no effect
//                                          but the intent is confusing

// CORRECT: write a word with only the target bit set
*irq_pending = IRQ_TX_COMPLETE;   // clears TX_COMPLETE, leaves RX_READY intact
```

## A Complete Register Map Example: 16550 UART

The 16550 UART is one of the most studied peripheral designs. Its registers demonstrate all the patterns above:

| Offset | Name | R/W | Description |
|---|---|---|---|
| +0 | RBR / THR | R / W | Receive Buffer / Transmit Holding |
| +1 | IER | R/W | Interrupt Enable Register |
| +2 | IIR / FCR | R / W | Interrupt ID / FIFO Control |
| +3 | LCR | R/W | Line Control (data bits, parity, stop bits) |
| +4 | MCR | R/W | Modem Control |
| +5 | LSR | R (W1C) | Line Status (data ready, errors, TX empty) |
| +6 | MSR | R (RC) | Modem Status |

Bit 0 of LSR (Data Ready) tells you a received byte is waiting. Bit 5 (THRE — Transmit Holding Register Empty) tells you it is safe to write the next byte.

## Using `struct` for Register Maps

Mapping a struct to a peripheral base address is idiomatic in embedded C:

```c
typedef struct {
    volatile uint8_t rbr_thr;  // +0
    volatile uint8_t ier;      // +1
    volatile uint8_t iir_fcr;  // +2
    volatile uint8_t lcr;      // +3
    volatile uint8_t mcr;      // +4
    volatile uint8_t lsr;      // +5
    volatile uint8_t msr;      // +6
    volatile uint8_t scr;      // +7  Scratch register
} UART16550_t;

#define LSR_DATA_READY  0x01
#define LSR_THRE        0x20

#define COM1  ((UART16550_t *)0x03F8)  // x86 port-mapped (conceptual MMIO analogy)

char uart_read(void) {
    while (!(COM1->lsr & LSR_DATA_READY))
        ;
    return COM1->rbr_thr;
}
```

## Common Pitfalls

- **Using `int` instead of `uint32_t`** — Sign extension when reading a register with bit 31 set gives a negative value, breaking flag checks.
- **Struct padding** — Compilers may insert padding between struct fields. Use `__attribute__((packed))` or verify the offsets with `static_assert`.
- **Shadow registers** — Some registers share an address but are selected by another register's state (e.g., 16550 RBR/THR share offset +0, DLL/DLH share +0/+1 when DLAB=1 in LCR).

> **Interview answer:** Device registers are small hardware memory locations that control and report the state of a peripheral. They come in control (CPU writes commands), status (CPU reads device state), and data varieties. Many use write-1-to-clear or read-to-clear semantics for interrupt flags, so software must understand the exact semantics of each register to avoid accidentally clearing bits or misreading state.
