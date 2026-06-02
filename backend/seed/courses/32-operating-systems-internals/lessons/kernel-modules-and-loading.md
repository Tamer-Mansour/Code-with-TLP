# Loadable Kernel Modules

A loadable kernel module (LKM) is a chunk of compiled kernel code that can be inserted into a running kernel at any time — without rebooting. This is how Linux ships drivers separately from the base kernel image and lets users add hardware support on demand.

## Why Modules?

- **Smaller kernel image** — only load drivers for present hardware.
- **Hot-plug support** — `udev` can automatically load a module when new hardware appears.
- **Easier development** — rebuild and reload a module in seconds instead of rebooting.
- **Third-party drivers** — vendors ship `.ko` files without modifying the kernel source.

## Anatomy of a Module

```c
#include <linux/module.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Ada Lovelace");
MODULE_DESCRIPTION("A minimal example kernel module");

static int __init my_module_init(void)
{
    printk(KERN_INFO "my_module: loaded\n");
    return 0;   /* non-zero = refuse to load */
}

static void __exit my_module_exit(void)
{
    printk(KERN_INFO "my_module: unloaded\n");
}

module_init(my_module_init);
module_exit(my_module_exit);
```

The `__init` annotation tells the linker to place the function in a special section discarded after boot (saves RAM). `__exit` is discarded if the module is built-in (not loadable).

## Building a Module

```makefile
# Minimal Makefile for an out-of-tree module
obj-m += my_module.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

```bash
make          # produces my_module.ko
```

The build system compiles the module against the *kernel headers* matching the running kernel, ensuring ABI compatibility.

## Loading and Unloading

```bash
# Low-level insert (no dependency resolution)
sudo insmod my_module.ko

# High-level insert (resolves dependencies from /lib/modules/)
sudo modprobe my_module

# List loaded modules
lsmod

# Remove a module
sudo rmmod my_module
sudo modprobe -r my_module

# Show module info (license, params, dependencies)
modinfo my_module.ko
```

## Module Parameters

Modules can accept parameters at load time:

```c
static int baud_rate = 9600;
module_param(baud_rate, int, 0644);
MODULE_PARM_DESC(baud_rate, "UART baud rate (default 9600)");
```

```bash
sudo modprobe my_uart baud_rate=115200
# Or after loading:
echo 115200 > /sys/module/my_uart/parameters/baud_rate
```

## Kernel Version and Symbols

Modules export symbols (functions, variables) using:

```c
EXPORT_SYMBOL(my_helper_function);        /* any license */
EXPORT_SYMBOL_GPL(my_private_function);   /* GPL-only callers */
```

A module's object file contains a `vermagic` string — a hash of the kernel ABI. Loading a module compiled against a different kernel version fails with:

```
ERROR: could not insert module: Invalid module format
```

This prevents subtle crashes from ABI mismatches.

## Common Pitfalls

- **Reference counting** — if another module depends on yours, `rmmod` will fail with `EBUSY`. Resolve the dependency order explicitly.
- **Forgetting to unregister resources** — if `module_exit` doesn't undo everything `module_init` did (device nodes, IRQs, memory), removal leaves the system in a dirty state.
- **GPL licensing** — using `EXPORT_SYMBOL_GPL` symbols in a non-GPL module causes load failure; check license compatibility.
- **`printk` rate limiting** — in hot paths use `pr_debug` or `dev_dbg` to avoid flooding the kernel log.

## Interview Answer

> **Q: What happens if you try to load a kernel module compiled against a different kernel version?**
>
> **Interview answer:** The kernel checks the module's `vermagic` string against the running kernel's ABI signature; a mismatch causes `insmod`/`modprobe` to reject the module with `Invalid module format` to prevent crashes from incompatible data structure layouts.
