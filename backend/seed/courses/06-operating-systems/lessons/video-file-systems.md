# Video: File Systems, Inodes, and Disk Scheduling

This video examines how file systems organize persistent data on disk, from the inode data structure to the Virtual File System (VFS) layer, and how the OS schedules disk I/O to maximize throughput.

## What This Video Covers

- File system abstractions: files, directories, hard links, and symbolic links
- The inode structure: metadata, direct/indirect block pointers, and how large files are addressed
- Directory implementation: linear list vs hash table vs B-tree
- The VFS (Virtual File System) layer and how it enables Linux to mount ext4, FAT32, and NFS simultaneously
- Disk scheduling algorithms: FCFS, SSTF, SCAN/C-SCAN, and LOOK/C-LOOK
- Journaling file systems and crash consistency (ext4, NTFS, APFS)
- Flash storage (SSDs) and why disk scheduling algorithms matter less on NVMe

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | File system goals and abstractions |
| ~15 min | Inodes and block addressing |
| ~35 min | Directories and path resolution |
| ~50 min | VFS layer |
| ~65 min | Disk scheduling algorithms |
| ~80 min | Journaling and crash consistency |
| ~90 min | SSD internals and implications |

## Key Takeaways

An **inode** stores all file metadata (permissions, timestamps, size, owner) and pointers to data blocks, but not the file name — names live in directory entries. The **VFS** abstraction lets the kernel present a unified `/` namespace across heterogeneous file systems. On spinning disks, the **SCAN** ("elevator") algorithm dramatically reduces seek time compared to FCFS; on SSDs, seek time is near-zero so scheduling primarily manages write amplification and wear leveling instead.
