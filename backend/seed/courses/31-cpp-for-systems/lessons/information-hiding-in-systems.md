# Information Hiding in Systems and Driver Code

**Information hiding** is the principle, articulated by David Parnas in 1972, that a module should hide its design decisions — especially the ones most likely to change. In systems and driver code this is not just good taste; it is a survival strategy. Hardware registers move. Kernel APIs change between versions. Protocol details differ across vendors.

## Why It Matters More at the Systems Level

At the application level a bad abstraction is annoying. At the systems level:

- A hardware register address baked into dozens of files becomes a weeks-long refactoring task when the SoC vendor revises the datasheet.
- An OS-specific call scattered across the codebase breaks every non-Linux port.
- A Linux kernel driver that exposes internal structures through `ioctl` payloads locks the kernel ABI permanently.

## Opaque Types: The C Equivalent of Pimpl

C has no classes, but it has the same technique via opaque pointers:

```c
// uart.h  — public API, no internals visible
typedef struct uart_dev uart_dev_t;  // incomplete type

uart_dev_t* uart_open(int port_num, int baud);
int         uart_write(uart_dev_t* dev, const uint8_t* buf, size_t len);
int         uart_read (uart_dev_t* dev,       uint8_t* buf, size_t len);
void        uart_close(uart_dev_t* dev);
```

```c
// uart.c  — implementation only, callers never see this
#include "uart.h"
#include <linux/serial.h>   // platform-specific

struct uart_dev {
    int fd;
    int baud;
    struct serial_struct cfg;
};

uart_dev_t* uart_open(int port_num, int baud) {
    uart_dev_t* d = malloc(sizeof *d);
    // ... open /dev/ttyS<port_num>, configure baud ...
    return d;
}
```

Callers hold a pointer to an incomplete type. They cannot dereference it, cannot compute `sizeof`, cannot copy it — the hardware-specific fields are completely hidden.

## Linux Kernel `file_operations`

The kernel itself is the largest example of information hiding in systems code. Every driver fills in a `struct file_operations` table:

```c
static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_release,
    .read    = my_read,
    .write   = my_write,
    .unlocked_ioctl = my_ioctl,
};
```

The VFS layer calls these function pointers without knowing anything about the underlying hardware. User-space calls `read()` on `/dev/mydevice` and is entirely unaware of DMA transfers, interrupt handlers, or register offsets. That is information hiding enforced by a function-pointer interface.

## Platform Abstraction Layers (PAL)

Embedded systems use a Platform Abstraction Layer to keep hardware details in one directory:

```
src/
  pal/
    stm32/gpio.c   <- STM32-specific register writes
    rpi/gpio.c     <- RPi memory-mapped GPIO
  pal/gpio.h       <- common interface both implement
  app/led_blink.c  <- calls gpio_set_high() with no platform knowledge
```

```c
// pal/gpio.h
void gpio_set_high(uint8_t pin);
void gpio_set_low (uint8_t pin);
int  gpio_read    (uint8_t pin);
```

The build system selects the right `pal/*.c` for the target. `led_blink.c` never changes when porting.

## `ioctl` and ABI Stability

A classic information-hiding failure: exposing a kernel `struct` in an `ioctl` header:

```c
// BAD: userspace now depends on this exact struct layout
struct my_ioctl_data {
    uint32_t reg_addr;   // hardware detail leaks to user space
    uint32_t value;
};
```

When the hardware adds a new field, the struct changes, and every user-space binary that uses this `ioctl` breaks. The fix is versioned, opaque command codes with stable payload formats and a version field the kernel can dispatch on.

## Key Practices

- **One file owns each hardware detail** — base address, register offsets, bit masks.
- **Platform headers stay inside `pal/`** — never `#include <linux/specific.h>` outside the PAL.
- **Version ioctl interfaces** — include a version/size field to allow future extension.
- **Minimize the public surface** — every symbol you expose is a promise you must keep.

## Interview Answer

> "Information hiding means isolating decisions that are likely to change — hardware addresses, OS APIs, protocol details — behind a stable interface. In driver and embedded code this is done with opaque pointer types, platform abstraction layers, and keeping platform-specific headers out of the shared API boundary."
