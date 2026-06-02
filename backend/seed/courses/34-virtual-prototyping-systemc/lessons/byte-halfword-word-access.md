# Byte, Halfword, and Word Accesses

Hardware buses and memory controllers do not expose a single monolithic view of memory. Instead, they support **access granularities** — the sizes at which you can independently read or write data. Understanding these sizes is essential for writing correct device drivers, memory-mapped I/O code, and accurate TLM transaction models.

## Standard Access Sizes

| Name | Width | C/C++ type (stdint.h) | ARM instruction |
|---|---|---|---|
| Byte | 8 bits (1 byte) | `uint8_t` | `LDRB` / `STRB` |
| Halfword | 16 bits (2 bytes) | `uint16_t` | `LDRH` / `STRH` |
| Word | 32 bits (4 bytes) | `uint32_t` | `LDR` / `STR` |
| Doubleword | 64 bits (8 bytes) | `uint64_t` | `LDRD` / `STRD` |

Some architectures (RISC-V, AArch64) also define 128-bit accesses for SIMD registers, but for embedded TLM work the four sizes above cover virtually all cases.

## Alignment Requirements

Most processors require that an N-byte access starts at an address that is a multiple of N.

```
Byte     → any address is valid
Halfword → address must be divisible by 2
Word     → address must be divisible by 4
```

Accessing a `uint32_t` at address `0x1001` is an **unaligned access**. On ARM Cortex-M (strict alignment), this raises a HardFault. On x86 it works but may be slower. In SystemC TLM models, peripheral models often check the address and byte-enable fields and respond with an error for misaligned transactions.

## Byte Enables

TLM-2.0 generic payloads carry a **byte enable** array alongside the data pointer. Each bit/byte in the enable array indicates whether the corresponding byte in the data buffer participates in the transfer.

```cpp
// Write only the low halfword (bytes 0 and 1) of a 4-byte word
uint8_t be[4] = { 0xFF, 0xFF, 0x00, 0x00 };
trans.set_byte_enable_ptr(be);
trans.set_byte_enable_length(4);
```

Byte enables are how a bus fabric implements sub-word writes on a word-wide bus — only the enabled byte lanes are actually written to the target.

## Worked Example: Reading a Status Register

A peripheral has a 32-bit status register at address `0x4000_0000`. Only bits [15:0] are implemented. A driver might:

```c
#include <stdint.h>

volatile uint32_t *const STATUS_REG = (uint32_t *)0x40000000U;
volatile uint16_t *const STATUS_LO  = (uint16_t *)0x40000000U;

/* Read the full word — upper 16 bits will read as 0 */
uint32_t full = *STATUS_REG;

/* Or read only the lower halfword directly */
uint16_t lo = *STATUS_LO;   /* valid only if peripheral supports halfword access */
```

Not all peripherals support sub-word reads. Check the datasheet — some require word-aligned, word-sized accesses only, and will return garbage or assert a bus error for narrower transfers.

## Sub-Word Writes: Read-Modify-Write

When a peripheral only supports word accesses but you need to change a single byte, you must perform a **read-modify-write**:

```c
uint32_t reg = *CTRL_REG;         /* 1. Read */
reg &= ~(0xFF << 8);              /* 2. Clear target byte */
reg |=  (0xAB << 8);              /* 3. Insert new value */
*CTRL_REG = reg;                  /* 4. Write back */
```

This sequence is **not atomic** — interrupts or DMA between the read and write can cause races. Use critical sections or atomic instructions when necessary.

## Common Pitfalls

- Assuming all peripherals support byte or halfword access — always check the datasheet.
- Forgetting that byte enables in TLM models interact with endianness: byte enable `[0]` always refers to the byte at the base address, which is the LSB in little-endian.
- Using `char *` arithmetic for pointer arithmetic on memory-mapped regions — always use `uint8_t *` to avoid sign-extension surprises.

## Interview Answer

> "Byte, halfword, and word accesses refer to 8-, 16-, and 32-bit memory transfers respectively. Hardware may require natural alignment (address divisible by transfer size), and sub-word writes to word-only peripherals must use a read-modify-write sequence. In TLM-2.0, byte enables let you express which bytes in a wider bus transfer are active."
