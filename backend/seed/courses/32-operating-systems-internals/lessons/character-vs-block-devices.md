# Character vs Block Devices

Unix organizes hardware into two fundamental categories based on how data flows through them. Understanding this distinction shapes every design decision in a driver.

## Character Devices

A character device transfers data as an **unbounded stream of bytes**, one byte (or a small chunk) at a time. There is no inherent notion of "blocks" or random-access positions.

**Examples:** serial ports (`ttyS0`), keyboards, mice, sensors, sound cards, framebuffers.

Key properties:
- Data is accessed sequentially (though `lseek` can be supported if it makes sense).
- No kernel-level buffer cache — data goes straight from driver to user space.
- Registered with `register_chrdev_region()` and a `file_operations` struct.

```c
static struct file_operations my_char_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_release,
    .read    = my_read,
    .write   = my_write,
    .poll    = my_poll,
};
```

## Block Devices

A block device exposes storage as an array of **fixed-size blocks** (typically 512 B or 4 KB). The kernel can read or write any block by its address at any time — true random access.

**Examples:** hard drives, SSDs, NVMe drives, SD cards, loop devices.

Key properties:
- Backed by the *block layer* and *page cache* — reads are often served from RAM without hitting hardware.
- The I/O scheduler can reorder and merge requests for efficiency.
- Partitioned into filesystems; the VFS sits on top.

```c
static struct block_device_operations my_blk_fops = {
    .owner          = THIS_MODULE,
    .open           = my_blk_open,
    .release        = my_blk_release,
    .ioctl          = my_blk_ioctl,
};
```

## Side-by-Side Comparison

| Property | Character Device | Block Device |
|---|---|---|
| Data unit | Byte stream | Fixed-size blocks |
| Random access | Optional | Mandatory |
| Kernel buffer cache | No | Yes (page cache) |
| I/O scheduler | No | Yes |
| Typical devices | Serial, keyboard, sensor | Disk, SSD, USB storage |
| `/dev` prefix letter | `c` | `b` |
| Registration call | `register_chrdev_region` | `register_blkdev` + `add_disk` |

## A Third Category: Network Devices

Network devices do not appear in `/dev` at all. They are accessed through sockets, not the filesystem. The driver registers a `net_device` structure and the kernel routes packets through the networking stack. This distinction is important for interviews.

## The Block Layer Request Path

When a user calls `write()` on a file:

```
write() syscall
    → VFS
    → Filesystem (ext4, xfs, …)
    → Page cache (may absorb the write)
    → Block layer (bio/request queue)
    → I/O scheduler (merges, reorders)
    → Block driver (submits to hardware)
    → DMA → Storage device
```

Character devices skip everything from the page cache downward.

## Worked Example: Choosing the Right Type

Suppose you are writing a driver for a temperature sensor that streams one reading per second:

- Data is naturally sequential — no need to seek to "block 42".
- No buffering benefit from a page cache.
- Choose **character device**.

Now suppose you are writing a driver for a RAM-backed virtual disk:

- User wants to format it with ext4 (requires block-level access).
- The kernel should be able to cache disk blocks in RAM.
- Choose **block device**.

## Common Pitfalls

- **Using a character device for disk-like storage** — the filesystem cannot sit on top of a character device; you must use a block device.
- **Forgetting `blk_mq_end_request()`** — block drivers must explicitly complete each I/O request or the I/O scheduler stalls.
- **Implementing `lseek` on a char device incorrectly** — if the device has no meaningful position, return `-ESPIPE` rather than silently ignoring it.

## Interview Answer

> **Q: What is the difference between a character device and a block device?**
>
> **Interview answer:** A character device exposes a sequential byte stream with no kernel buffering (e.g., serial port), while a block device exposes randomly addressable fixed-size blocks backed by the page cache and I/O scheduler (e.g., hard drive) — the distinction determines whether a filesystem can be placed on top.
