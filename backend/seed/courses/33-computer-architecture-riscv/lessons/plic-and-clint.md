# PLIC and CLINT: Interrupt Controllers

The RISC-V ISA defines the signaling mechanism for interrupts through CSRs, but it does not specify how external devices are connected or how multiple simultaneous interrupts are prioritized. Two standard platform components fill this gap: the **CLINT** for core-local timer and software interrupts, and the **PLIC** for all external device interrupts.

## The CLINT (Core-Local Interruptor)

The CLINT is a memory-mapped peripheral present on virtually every RISC-V platform. It provides two interrupt sources per hart:

- **Machine Timer Interrupt** (`mip.MTIP`) — generated when `mtime >= mtimecmp`.
- **Machine Software Interrupt** (`mip.MSIP`) — set by writing to a register; used for IPI (Inter-Processor Interrupt).

### CLINT Memory Map (SiFive-compatible)

| Offset | Width | Name | Description |
|---|---|---|---|
| `0x0000` | 32-bit | `msip[0]` | Software interrupt for hart 0 |
| `0x0004` | 32-bit | `msip[1]` | Software interrupt for hart 1 |
| `0x4000` | 64-bit | `mtimecmp[0]` | Timer compare value for hart 0 |
| `0x4008` | 64-bit | `mtimecmp[1]` | Timer compare value for hart 1 |
| `0xBFF8` | 64-bit | `mtime` | Global free-running counter |

The `mtime` counter increments at a platform-specific frequency (e.g., 10 MHz on QEMU's virt machine, 32.768 kHz on some embedded boards). The comparison is unsigned 64-bit.

```c
#define CLINT   ((volatile uint8_t*)0x02000000UL)
#define MTIME       (*(volatile uint64_t*)(CLINT + 0xBFF8))
#define MTIMECMP(n) (*(volatile uint64_t*)(CLINT + 0x4000 + 8*(n)))
#define MSIP(n)     (*(volatile uint32_t*)(CLINT + 0x0000 + 4*(n)))

// Schedule a timer interrupt 1 second from now (10 MHz CLINT)
void schedule_timer_1s(int hart) {
    MTIMECMP(hart) = MTIME + 10000000ULL;
}

// Send IPI to hart 1
void send_ipi(int hart) {
    MSIP(hart) = 1;
}
```

**Clearing CLINT interrupts:**
- Timer: write a new `mtimecmp` value in the future. `mip.MTIP` is hardware-controlled.
- Software: write `0` to the `msip` register of your own hart from within the ISR.

## The PLIC (Platform-Level Interrupt Controller)

The PLIC manages external interrupts from devices (UART, SPI, Ethernet, GPIO, etc.) and presents a single `mip.MEIP` signal to each hart. It arbitrates priority among potentially hundreds of interrupt sources.

### PLIC Concepts

| Concept | Description |
|---|---|
| **Source** | A numbered device interrupt (1..N, where 0 is reserved) |
| **Priority** | A per-source 32-bit value (higher = more urgent) |
| **Enable** | Per-context bitmask of which sources are enabled |
| **Threshold** | Per-context value; only interrupts with priority > threshold are forwarded |
| **Claim** | Read to get the highest-priority pending interrupt ID |
| **Complete** | Write the ID back to signal servicing is done |

### PLIC Memory Map (SiFive-compatible, base 0x0C000000)

| Offset | Description |
|---|---|
| `0x000000 + 4*N` | Priority for source N |
| `0x001000` | Interrupt pending bits (read-only, 1 bit per source) |
| `0x002000 + context*0x80` | Enable bits for context (hart × mode) |
| `0x200000 + context*0x1000` | Priority threshold for context |
| `0x200004 + context*0x1000` | Claim / complete register |

```c
#define PLIC_BASE         0x0C000000UL
#define PLIC_PRIORITY(n)  (*(volatile uint32_t*)(PLIC_BASE + 4*(n)))
#define PLIC_PENDING(n)   (*(volatile uint32_t*)(PLIC_BASE + 0x1000 + 4*(n)/32))
// Context 0 = hart 0 M-mode; context 1 = hart 0 S-mode; context 2 = hart 1 M-mode ...
#define PLIC_ENABLE(ctx,n)   /* word-addressed enable bits */
#define PLIC_THRESHOLD(ctx)  (*(volatile uint32_t*)(PLIC_BASE + 0x200000 + (ctx)*0x1000))
#define PLIC_CLAIM(ctx)      (*(volatile uint32_t*)(PLIC_BASE + 0x200004 + (ctx)*0x1000))
#define PLIC_COMPLETE(ctx)   (*(volatile uint32_t*)(PLIC_BASE + 0x200004 + (ctx)*0x1000))
```

### PLIC Initialization Sequence

```c
void plic_init(void) {
    int ctx = 0;  // hart 0, M-mode

    // Step 1: Set priority for each interrupt source
    PLIC_PRIORITY(UART0_IRQ) = 1;   // UART has priority 1
    PLIC_PRIORITY(GPIO_IRQ)  = 2;   // GPIO has higher priority

    // Step 2: Enable sources for this context
    // (set bit N in the enable word at offset 0x2000)
    *(volatile uint32_t*)(PLIC_BASE + 0x2000) |= (1 << UART0_IRQ)
                                                | (1 << GPIO_IRQ);

    // Step 3: Set threshold (0 = forward all priorities > 0)
    PLIC_THRESHOLD(ctx) = 0;
}
```

### PLIC Claim/Complete Cycle

```c
void external_interrupt_handler(void) {
    int ctx = 0;
    uint32_t irq = PLIC_CLAIM(ctx);   // atomically claim the interrupt
    if (irq == 0) return;              // 0 means no interrupt pending (spurious)

    switch (irq) {
        case UART0_IRQ: handle_uart(); break;
        case GPIO_IRQ:  handle_gpio(); break;
        default: break;
    }

    PLIC_COMPLETE(ctx) = irq;          // signal completion; unmask this source
}
```

The claim is a **single atomic read**: it simultaneously returns the IRQ ID and acknowledges receipt to the PLIC. The complete write re-enables the source for future interrupts.

## CLINT vs PLIC at a Glance

| Property | CLINT | PLIC |
|---|---|---|
| Interrupt sources | Timer, software (per-hart) | External devices (up to 1023) |
| Priority arbitration | None (single source per type) | Yes, per-source priority + threshold |
| `mip` bit it sets | MTIP, MSIP | MEIP |
| Clearing mechanism | Update `mtimecmp` / write `msip=0` | Claim then complete |
| Required? | Yes (virtually always) | Yes for external devices |

> **Interview answer:** The CLINT provides per-hart timer (`mtime/mtimecmp`) and software interrupts (`msip`). The PLIC collects all external device interrupts, prioritizes them, and presents a single `mip.MEIP` signal. An ISR services PLIC interrupts by claiming the highest-priority IRQ, servicing the device, then completing the transaction.

## Common Pitfalls

- Not completing a PLIC claim — the source remains masked and future interrupts from that device are silently dropped.
- 64-bit `mtime`/`mtimecmp` on RV32: write the high word first with `0xFFFFFFFF` as a guard, write the low word, then write the correct high word to avoid a spurious timer interrupt during the sequence.
- Setting PLIC threshold too high — sources with priority ≤ threshold are never forwarded to the hart.
