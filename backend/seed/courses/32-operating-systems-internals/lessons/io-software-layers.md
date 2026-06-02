# The I/O Software Stack and Buffering

Between a user process calling `read()` and electrons moving on a bus, there are five or six distinct software layers. Each layer isolates the one above it from details the one above should not care about.

## The Layer Model

```
User Process         read(fd, buf, n)
─────────────────────────────────────────────
POSIX I/O Library    buffered I/O (FILE*, fread), syscall wrappers
─────────────────────────────────────────────
VFS (Virtual FS)     file / inode / dentry abstraction
─────────────────────────────────────────────
Block / Char Layer   request queues, elevator, plug/unplug
─────────────────────────────────────────────
Device Driver        programs MMIO registers, sets up DMA
─────────────────────────────────────────────
Hardware             controller, bus, device
```

## Layer 1: User-Space I/O Library

`fread()` / `fwrite()` (C standard library) maintain a **user-space buffer** (typically 4–8 KB). Multiple small application reads are satisfied from this buffer without syscalls. Only when the buffer is empty does the library issue `read()` into the kernel.

This is **double-buffering**: kernel has its page cache, library has its `FILE` buffer. Both reduce system call overhead.

## Layer 2: VFS — Virtual File System

The VFS presents a uniform interface (`open`, `read`, `write`, `ioctl`) regardless of whether the underlying storage is ext4, NFS, tmpfs, or a character device. It resolves pathnames to **inodes**, checks permissions, and dispatches to the concrete filesystem.

## Layer 3: Page Cache

For block devices, the kernel maintains a **page cache**: recently read/written 4 KB pages. A `read()` first checks the page cache; if the page is present (cache hit), data is copied to user space immediately without touching the disk or DMA. A **dirty page** is one written by the CPU but not yet flushed to disk; a **writeback thread** (`kworker/flush`) periodically syncs dirty pages.

```
read() hit:   [VFS] --> page cache --> copy_to_user() -- no I/O
read() miss:  [VFS] --> page cache miss --> submit_bio() --> driver --> DMA --> page cache --> copy_to_user()
```

## Layer 4: Block Layer and I/O Scheduler

For block device misses, the VFS submits a **bio** (block I/O request). The block layer:

- **Merges** adjacent requests (elevator / scheduler) to reduce seeks on HDDs.
- **Queues** requests (multi-queue block layer, `blk-mq` in Linux).
- Dispatches to the driver when the device has capacity.

Common I/O schedulers:

| Scheduler | Best for |
|---|---|
| None (FIFO) | NVMe SSDs (no seek penalty) |
| mq-deadline | SSDs with latency guarantee |
| BFQ | Desktop HDDs (bandwidth fairness) |
| Kyber | Fast SSDs, low latency |

## Layer 5: Device Driver

The driver translates a `bio` into device-specific commands: programs MMIO registers, populates DMA descriptors, kicks off the transfer, and handles the completion interrupt. This is the lowest software layer.

## Buffering Strategies

| Strategy | Description | Used in |
|---|---|---|
| **No buffering** | Every byte goes straight to the device | Raw serial ports, `O_DIRECT` |
| **User-space buffering** | `FILE *` buffer, flush on full/newline/explicit | `fwrite`, `printf` |
| **Kernel buffering (page cache)** | Kernel caches blocks, writeback in background | All normal file I/O |
| **Double buffering** | Two buffers; device fills one while CPU drains the other | Audio, video capture |
| **Ring buffer** | Producer/consumer FIFO; efficient for streaming | Network RX/TX rings, audio ALSA |

## `O_DIRECT` — Bypassing the Page Cache

Some applications (databases) manage their own caching. They open files with `O_DIRECT` to bypass the kernel page cache entirely and issue DMA straight to their own aligned buffers:

```c
int fd = open("db.data", O_RDONLY | O_DIRECT);
// buf must be aligned to 512 bytes (or sector size)
posix_memalign(&buf, 512, 4096);
read(fd, buf, 4096);
```

Bypassing the cache means no double-copy (disk -> page cache -> user buf) but also no cache warming across reads.

## `ioctl` — The Escape Hatch

When no standard syscall models a device operation (set baud rate, query NIC statistics, lock a SCSI tape), drivers expose **ioctl** (I/O control) commands. Each driver defines its own command codes:

```c
struct ifreq ifr;
strncpy(ifr.ifr_name, "eth0", IFNAMSIZ);
ioctl(sock_fd, SIOCGIFADDR, &ifr);   // get interface IP address
```

> **Interview answer:** The I/O software stack layers user-space library buffering, the VFS, the page cache, the block I/O scheduler, and the device driver. Each layer adds a level of abstraction and a buffering opportunity. The page cache is the most impactful for performance: reads hit warm cache in microseconds rather than waiting milliseconds for disk DMA.
