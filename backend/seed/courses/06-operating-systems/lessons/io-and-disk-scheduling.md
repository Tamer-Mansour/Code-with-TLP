# I/O Systems and Disk Scheduling

I/O is the slowest part of most systems. The OS must bridge a 100,000× speed gap between RAM (~100 ns) and spinning disks (~10 ms), manage dozens of heterogeneous devices, and present them all through a uniform interface. The mechanisms it uses — device drivers, DMA, buffering, and scheduling — are the difference between a responsive system and a thrashing one.

## The I/O Hardware Stack

```
Application
    │  open/read/write syscalls
    ▼
VFS Layer (Virtual File System)
    │  file_operations.read_iter()
    ▼
File System Driver (ext4, NTFS, btrfs …)
    │  submits block I/O requests (struct bio in Linux)
    ▼
Block Layer (I/O Scheduler)
    │  merges and reorders requests for efficiency
    ▼
Device Driver (SCSI, NVMe, SATA, USB …)
    │  programs DMA controller or issues port I/O commands
    ▼
Hardware Controller (HDD, SSD, NIC, keyboard …)
    │  (interrupt or polling when done)
    ▼
CPU interrupt handler → wake up waiting process
```

Each layer adds abstraction. The VFS does not know if it is talking to ext4 on a local SSD or NFS over a network; ext4 does not know if the block device is a spinning disk or an NVMe SSD.

## Device Categories

| Category | Examples | Transfer Unit | Typical Access Latency |
|----------|----------|--------------|----------------------|
| Block | HDD, SSD, USB drive | Fixed blocks (512B–4KB) | 0.1–10 ms |
| Character | Keyboard, serial port, /dev/random | Byte stream | Event-driven |
| Network | NIC, Wi-Fi adapter | Packets | Variable |
| Memory-mapped | GPU framebuffer, PCI-e device BAR | Direct memory | ~50–200 ns |

Block devices expose a flat array of fixed-size blocks. The file system decides how to map logical file structure onto physical blocks.

## Direct Memory Access (DMA)

Without DMA, the CPU would copy every byte between a device and RAM — wasting precious cycles:

```
Without DMA (Programmed I/O):
  CPU: write 1 byte → device register
  CPU: write 1 byte → device register
  ... (repeat 4096× for a 4KB block)
  CPU busy entire time — cannot run any other process

With DMA:
  1. CPU programs DMA controller:
     "read 4KB from disk LBA 5000 → physical addr 0xA000"
  2. DMA controller operates on the memory bus independently
  3. CPU: marks requesting process as WAITING, runs other processes
  4. DMA: fetches data, places it in RAM at 0xA000
  5. DMA: raises hardware interrupt when done
  6. CPU: interrupt handler runs → marks process READY
  7. Process resumes, reads from 0xA000
```

DMA is used for all high-throughput devices: NIC (network cards), SSDs (NVMe via PCIe DMA), GPUs, sound cards. Modern NVMe SSDs can sustain 7 GB/s of sequential reads using multiple DMA channels.

## Spinning Disk (HDD) Geometry

Although SSDs are now dominant, understanding HDD mechanics explains why disk scheduling matters:

```
HDD cross-section:
  ┌─────────────────────────────────────────┐
  │  Platter 1 (top)     ← spinning @7200rpm│
  │    Track 0 (outer)                      │
  │    Track 1                              │
  │    ...                                  │
  │    Track 999 (inner)                    │
  ├─────────────────────────────────────────┤
  │  Platter 2 (bottom)                     │
  └─────────────────────────────────────────┘
  Read/write head on actuator arm moves radially
  Cylinder = same track number across all platters
```

**Access time** for a single read:
```
Total = Seek time + Rotational latency + Transfer time
      ≈ 5 ms     +    4 ms             +   0.1 ms
      ≈ 9 ms  (this is 9,000,000 ns — compare to 1 ns for L1 cache!)
```

Seek time dominates — the actuator arm physically moves to the target track. Minimizing total arm movement across all pending requests is the goal of disk scheduling.

## Disk Scheduling Algorithms

### FCFS (First Come, First Served)

Service requests in arrival order. Fair but random arm movement.

```
Head at cylinder 53, queue: [98, 183, 37, 122, 14, 124, 65, 67]

Service order: 53→98→183→37→122→14→124→65→67
Arm movement:   45  85  146  85  108  110  59  2  = 640 cylinders total
```

### SSTF (Shortest Seek Time First)

Always service the request nearest to the current head position.

```
Head at 53, queue: [98, 183, 37, 122, 14, 124, 65, 67]

From 53: nearest is 65 (12 away) → move to 65
From 65: nearest is 67 (2) → 67
From 67: nearest is 37 (30) → 37 (not 98 which is 31 away)
From 37: nearest is 14 (23) → 14
From 14: nearest is 98 (84) → 98
From 98: nearest is 122 (24) → 122
From 122: nearest is 124 (2) → 124
From 124: nearest is 183 (59) → 183

Total movement: 12+2+30+23+84+24+2+59 = 236 cylinders
```

Improvement over FCFS, but risk of **starvation** for requests at the far end if nearby requests keep arriving.

### SCAN (Elevator Algorithm)

Head sweeps in one direction, servicing all requests en route, then reverses.

```
Head at 53, direction: ascending, queue: [98, 183, 37, 122, 14, 124, 65, 67]

Sort requests: [14, 37, 65, 67, 98, 122, 124, 183]
Ascending pass: 53→65→67→98→122→124→183→[reverse]
Descending pass: →37→14

Service order: 65, 67, 98, 122, 124, 183, 37, 14
Total movement: (183-53) + (183-14) = 130 + 169 = 299 cylinders
```

### C-SCAN (Circular SCAN)

Like SCAN but only services requests in one direction (ascending). After reaching the end, jumps back to the beginning (near cylinder 0) without servicing on the return.

```
Head at 53, ascending, queue: [98, 183, 37, 122, 14, 124, 65, 67]

Ascending pass: 53→65→67→98→122→124→183→[jump to 0]→14→37

Total movement: (183-53) + (183-0) + 37 = 130 + 183 + 37 = 350 cylinders
(higher total movement but MORE UNIFORM wait time across all requests)
```

### Comparison

| Algorithm | Seek Distance | Fairness | Starvation Risk |
|-----------|--------------|---------|----------------|
| FCFS | High | Perfect arrival order | None |
| SSTF | Low | Poor (favors center) | Yes |
| SCAN | Medium | Good | No |
| C-SCAN | Medium | Best (uniform) | No |

**NVMe SSDs:** have no moving parts, ~0.1ms access time regardless of "cylinder." Disk scheduling algorithms are largely irrelevant for SSDs — NVMe drivers use a simpler multi-queue model (`blk-mq`) where each CPU core has its own submission queue.

## I/O Buffering and the Page Cache

The OS maintains a **page cache** (buffer cache) — a pool of RAM that caches recently-used disk blocks. In Linux, the page cache is unified with the VM system: file data, directory data, and mmapped files all live in the same cache.

```
read("file.txt", buf, 4096):
  1. VFS → ext4 → check page cache:
     HIT:  copy from page cache → user buf (nanoseconds)
     MISS: submit block I/O request
           → DMA reads 4KB from disk into page cache
           → copy page cache → user buf (milliseconds first time)
           (future reads of same block: nanoseconds from cache)

write("file.txt", buf, 4096):
  1. Copy user buf → page cache (write is done from app's perspective)
  2. Mark page as DIRTY (not yet on disk)
  3. Return immediately to application
  4. Background: pdflush/writeback daemon flushes dirty pages to disk
     periodically (every ~5 seconds or when page cache pressure is high)
```

**Write-back caching** (default) gives much better write performance at the cost of a small data loss window. `fsync(fd)` forces all dirty pages for a file to disk immediately.

**Direct I/O** (`O_DIRECT` flag on Linux): bypasses the page cache entirely. Used by databases (PostgreSQL, MySQL) that manage their own buffer pool — they don't want the OS double-caching their data.

## I/O Notification: Interrupts vs. Polling

| Method | How It Works | Overhead | Use Case |
|--------|-------------|----------|----------|
| **Interrupts** | Device raises IRQ when done; CPU stops current work to handle it | Per-I/O interrupt cost (~10 µs) | HDD, keyboard, NIC at low/medium I/O rates |
| **Polling** | CPU repeatedly checks a device register in a tight loop | Burns CPU cycles between I/Os | NVMe SSD at millions of IOPS — interrupt overhead would dominate |
| **Hybrid (busy-wait then sleep)** | Poll briefly, then fall back to interrupt if too long | Best of both | Modern NVMe drivers: `blk-mq` with `IORING_SETUP_IOPOLL` |

Modern Linux `io_uring` (since kernel 5.1) supports a **submission queue polling** mode where a dedicated kernel thread continuously polls NVMe submission queues, achieving sub-20µs I/O latency without any system call after initial setup.

## Asynchronous I/O

Traditional `read()` is synchronous: the calling process blocks until data arrives. Asynchronous I/O decouples submission from completion:

```
POSIX AIO or Linux io_uring:
  1. Submit 100 read requests in one batch
  2. Application continues doing other work
  3. Poll or wait for completions (event-driven)
  4. Handle each completion as it arrives

vs. synchronous:
  for each file: read() → block → handle → repeat
  (1 request in-flight at a time)
```

Async I/O enables servers to saturate a fast SSD (which can handle 1M+ IOPS) with a single thread, rather than needing 1000 threads (one per in-flight I/O).

## Practical Benchmarking

```bash
# Sequential read speed (bypassing page cache with O_DIRECT)
dd if=/dev/sda bs=1M count=1024 iflag=direct

# Random IOPS measurement
fio --name=randread --ioengine=libaio --iodepth=32 \
    --rw=randread --bs=4k --size=10G --filename=/dev/nvme0n1

# Page cache stats
cat /proc/meminfo | grep -E 'Cached|Buffers|SwapCached'

# I/O wait fraction (% of time CPU waited for I/O)
iostat -x 1
```

## Key Takeaways

- The I/O stack layers application calls down through VFS → file system → block layer → driver → hardware.
- **DMA** lets devices transfer data to/from RAM without CPU involvement, freeing the CPU to run other processes.
- HDD scheduling algorithms (SSTF, SCAN, C-SCAN) minimize arm movement to reduce latency; irrelevant for SSDs.
- The **page cache** dramatically reduces disk I/O by keeping hot blocks in RAM; writes are buffered and flushed asynchronously.
- `fsync()` forces dirty pages to disk — essential for durability (databases call it after every transaction).
- Modern `io_uring` + NVMe polling achieves sub-20µs I/O latency with zero system calls per request after setup.
