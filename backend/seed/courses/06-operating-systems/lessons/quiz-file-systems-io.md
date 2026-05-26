# Quiz: File Systems & I/O

**Q1. What does an inode store, and what does it NOT store?**

- [ ] The file name and a list of all data blocks; it does NOT store permissions
- [x] File metadata (permissions, size, timestamps, block pointers) but NOT the file name
- [ ] The directory tree structure and all subdirectory inode numbers
- [ ] The file's data directly, but only for files smaller than one block

**Q2. Where is a file's name stored in a Unix file system?**

- [ ] In the inode, in a name field alongside the other metadata
- [x] In the directory entry that references the inode
- [ ] In the first data block of the file, as a null-terminated string
- [ ] In the file system superblock's global name table

**Q3. A hard link and a symbolic link differ in that:**

- [ ] A hard link stores a path string; a symbolic link stores an inode number
- [x] A hard link is a directory entry pointing directly to an inode (no data copy); a symbolic link is its own inode containing a path string
- [ ] A hard link can cross file system boundaries; a symbolic link cannot
- [ ] A hard link can reference directories; a symbolic link cannot

**Q4. What is the purpose of the Virtual File System (VFS) layer?**

- [ ] To encrypt file data transparently before writing it to block devices
- [ ] To compress disk blocks on the fly to extend available storage capacity
- [x] To provide a uniform interface so applications work identically with any file system (ext4, btrfs, tmpfs, NFS) without modification
- [ ] To cache frequently accessed files in GPU memory for faster rendering

**Q5. DMA (Direct Memory Access) improves I/O performance by:**

- [ ] Compressing data before writing it to disk to reduce the number of blocks needed
- [x] Allowing devices to transfer data directly to and from RAM without the CPU copying each byte, freeing the CPU to run other processes
- [ ] Giving the disk controller its own dedicated CPU core to handle I/O concurrently
- [ ] Caching disk blocks in a separate battery-backed NVRAM chip on the motherboard

**Q6. The SCAN (Elevator) disk scheduling algorithm services requests by:**

- [ ] Always servicing the request whose sector number is closest to the current head
- [x] Moving the disk head in one direction servicing all pending requests, then reversing — like an elevator going up then down
- [ ] Servicing requests in strict arrival order to guarantee fairness
- [ ] Moving in one direction only and jumping back to the innermost track after each pass
