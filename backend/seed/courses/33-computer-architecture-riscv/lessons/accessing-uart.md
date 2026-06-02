# Accessing a UART via MMIO

A UART (Universal Asynchronous Receiver-Transmitter) is almost always the first peripheral a bare-metal RISC-V programmer touches. It provides a simple serial channel for debugging output long before any OS or display subsystem is running. Most RISC-V development platforms expose a 16550-compatible UART at a known MMIO address.

## 16550 Register Map

The 16550 UART exposes its interface through eight 8-bit registers, all accessible as byte-wide MMIO offsets from a base address:

| Offset | Name | Direction | Purpose |
|---|---|---|---|
| +0 | RBR / THR | R / W | Receive Buffer / Transmit Holding |
| +1 | IER | R/W | Interrupt Enable Register |
| +2 | IIR / FCR | R / W | Interrupt ID / FIFO Control |
| +3 | LCR | R/W | Line Control (data bits, parity, stop) |
| +4 | MCR | R/W | Modem Control |
| +5 | LSR | R | Line Status Register |
| +6 | MSR | R | Modem Status |
| +7 | SCR | R/W | Scratch Register |

The **LSR** (offset +5) is the key polling register: bit 5 (`THRE`) is set when the transmit FIFO is empty and ready to accept a new byte.

## Minimal Polling Driver in C

```c
#include <stdint.h>

#define UART0_BASE  0x10000000UL

/* MMIO register pointers */
volatile uint8_t * const UART_THR = (volatile uint8_t *)(UART0_BASE + 0); // Transmit
volatile uint8_t * const UART_LSR = (volatile uint8_t *)(UART0_BASE + 5); // Status

#define LSR_THRE  (1u << 5)   /* Transmit Holding Register Empty */
#define LSR_DR    (1u << 0)   /* Data Ready (byte received) */

/* Send one character — spin until THR is empty */
void uart_putc(char c) {
    while (!(*UART_LSR & LSR_THRE))
        ;
    *UART_THR = (uint8_t)c;
}

/* Receive one character — spin until data is ready */
char uart_getc(void) {
    while (!(*UART_LSR & LSR_DR))
        ;
    return (char)*UART_THR;  /* Reading RBR clears the data-ready flag */
}

/* Send a null-terminated string */
void uart_puts(const char *s) {
    while (*s)
        uart_putc(*s++);
}
```

## Initialization Sequence

Before using the UART on real hardware (QEMU sets sane defaults, so init is optional there), you must configure the baud rate divisor and line parameters:

```c
#define UART_DLL  (volatile uint8_t *)(UART0_BASE + 0)  // Divisor LSB (when DLAB=1)
#define UART_DLM  (volatile uint8_t *)(UART0_BASE + 1)  // Divisor MSB (when DLAB=1)
#define UART_LCR  (volatile uint8_t *)(UART0_BASE + 3)
#define UART_FCR  (volatile uint8_t *)(UART0_BASE + 2)

void uart_init(uint32_t clock_hz, uint32_t baud) {
    uint16_t divisor = (uint16_t)(clock_hz / (16 * baud));

    *UART_LCR = 0x80;           // Set DLAB to access divisor registers
    *UART_DLL = divisor & 0xFF;
    *UART_DLM = divisor >> 8;
    *UART_LCR = 0x03;           // 8N1: 8 data bits, no parity, 1 stop bit
    *UART_FCR = 0x07;           // Enable and clear FIFOs
}
```

## Assembly: Writing One Byte

In RISC-V assembly the same polling loop looks like this:

```asm
# a0 = character to send
# Assumes UART_BASE and offsets are known constants
uart_putc:
    li   t0, 0x10000000     # UART base address
    li   t1, 0x20            # LSR_THRE = bit 5
.wait:
    lbu  t2, 5(t0)           # Read LSR (byte-wide)
    and  t2, t2, t1
    beqz t2, .wait           # Loop while THR not empty
    sb   a0, 0(t0)           # Store byte to THR
    ret
```

## Common Pitfalls

- **Using `lw` instead of `lb`/`lbu`.** 16550 registers are 8-bit; a 32-bit load reads neighboring registers and produces wrong results.
- **Skipping DLAB clear.** If you forget to clear the DLAB bit after setting the divisor, subsequent writes go to the divisor, not the THR.
- **No `fence` in multi-hart systems.** If another hart or DMA engine might also touch UART registers, a `fence` before and after the burst protects ordering.

## Interview Answer

> "Poll bit 5 (THRE) of the Line Status Register at base+5. When it is set the transmit FIFO is empty; write the character byte to base+0 (THR). All accesses must be byte-wide `volatile` loads/stores to avoid compiler and hardware misinterpretation."
