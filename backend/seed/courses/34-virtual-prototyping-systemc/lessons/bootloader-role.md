# The Bootloader's Role (U-Boot)

U-Boot (Universal Boot Loader) is the dominant open-source bootloader for embedded Linux systems. In a virtual platform, U-Boot is often the first piece of complex software that exercises many peripheral models simultaneously, making it a key validation milestone.

## What U-Boot Does

U-Boot bridges the gap between low-level hardware initialization and the Linux kernel. Its responsibilities include:

- Initializing DRAM, caches, and the MMU
- Enumerating and initializing peripherals (UART, Ethernet, USB, storage)
- Loading the kernel image and device tree blob (DTB) into DRAM
- Optionally running a boot script or interactive command shell
- Jumping to the kernel entry point with the correct CPU state

**Interview answer:** U-Boot is the final bootloader stage; it initializes peripherals, loads the kernel and DTB into DRAM, then jumps to the kernel entry address with register conventions the kernel expects (e.g., x0 = DTB address in ARMv8).

## U-Boot and the VP: What Models Must Exist

Running U-Boot on a VP requires at minimum:

| Peripheral | Why U-Boot Needs It |
|---|---|
| UART | Console output; U-Boot's `printf` goes here |
| Timer / System Counter | Timeouts, delay loops, `udelay()` |
| DRAM controller | Memory test, relocation |
| Interrupt controller | Some boards use interrupts for storage |
| Storage (eMMC/QSPI) | Reading kernel from media (or pre-loaded) |

If any of these is missing or returns wrong values, U-Boot will stall, panic, or produce incorrect output.

## Relocation: A Frequent Source of VP Bugs

U-Boot copies itself from its load address to the **top of DRAM** during startup (called **relocation**). After relocation, all global variables and function pointers are at new addresses. This stresses the VP's DRAM model:

```
U-Boot starts at: 0x0200_0000  (BL33 load address)
U-Boot relocates to: 0x7F00_0000  (top of 2 GB DRAM)
```

If the VP's DRAM model does not cover the relocation region, U-Boot will write to an unmapped address. The bus model should return `TLM_ADDRESS_ERROR_RESPONSE` and the error should be visible in the VP log.

## Interacting with U-Boot via Virtual UART

The VP's UART model connects to a TCP socket or a POSIX pseudo-terminal (PTY). This lets you interact with U-Boot's command shell:

```bash
# On the host, connect to the VP's UART:
telnet localhost 5000

# Inside U-Boot shell:
U-Boot> printenv bootargs
U-Boot> bootm 0x40000000 - 0x4FA00000
```

Being able to drive U-Boot commands from a script is essential for automated VP regression testing.

## U-Boot Environment Variables

U-Boot reads its environment (boot commands, addresses, flags) from a storage region. In a VP, it is easiest to supply this via a pre-built environment binary or to compile U-Boot with `CONFIG_ENV_IS_NOWHERE` so it uses defaults:

```c
// In U-Boot board config (include/configs/my_vp_board.h):
#define CONFIG_ENV_IS_NOWHERE   1
#define CONFIG_BOOTCOMMAND      \
    "booti 0x40000000 - 0x4FA00000"
```

This removes the need to model the environment storage medium accurately during early bring-up.

## Common Pitfalls

- **Timer model returns zero**: U-Boot's `udelay()` and timeout loops read a free-running timer. If the timer register always reads 0, every timeout expires immediately, causing spurious failures or infinite loops.
- **UART model not acknowledging TX FIFO empty**: U-Boot polls the UART status register waiting for the transmit FIFO to drain. If the VP's UART model never sets the FIFO-empty bit, the console hangs after the first character.
- **Cache operations on non-existent cache model**: U-Boot calls `dcache_enable()` and cache-flush operations. If the VP has no cache model, these TLM transactions must be absorbed silently (returned OK) rather than triggering an error.

## Worked Example: Minimal UART Model for U-Boot

```cpp
void UartModel::b_transport(tlm::tlm_generic_payload& gp,
                            sc_core::sc_time& delay) {
    uint32_t offset = gp.get_address();
    uint8_t  val    = *gp.get_data_ptr();

    if (gp.get_command() == tlm::TLM_WRITE_COMMAND) {
        if (offset == UART_TX_REG) {
            std::cout << static_cast<char>(val) << std::flush;
        }
    } else { // READ
        if (offset == UART_STATUS_REG) {
            // Always report TX empty, RX empty
            uint8_t status = UART_TX_EMPTY;
            std::memcpy(gp.get_data_ptr(), &status, 1);
        }
    }
    gp.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

This minimal model prints characters to `stdout` and always reports the TX FIFO as empty — enough for U-Boot's console to work.
