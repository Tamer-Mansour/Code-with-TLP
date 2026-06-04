# Quiz: Distributed Systems and Advanced Topics

**Q1. NFS (Network File System) is described as "stateless." What does this mean?**

- [ ] NFS does not support file writes — it is read-only
- [ ] The NFS client keeps no cache; every read goes to the server
- [x] The NFS server keeps no per-client session state between requests; every RPC carries enough context to be processed independently
- [ ] NFS files have no metadata (no inode, no timestamps)

**Q2. AFS (Andrew File System) improves read performance compared to NFS primarily through:**

- [ ] Striping file data across multiple server disks (RAID-like)
- [x] Callback-based caching — the client caches entire files locally and the server promises to notify (break the callback) on any modification
- [ ] Using UDP instead of TCP for lower-latency small reads
- [ ] Compressing all file data before sending it over the network

**Q3. The CAP theorem states that a distributed system can guarantee at most two of: Consistency, Availability, and Partition tolerance. In practice, network partitions cannot be eliminated, so distributed systems must choose between:**

- [ ] Consistency and Availability (sacrifice partition tolerance)
- [x] Consistency (CP) or Availability (AP) — partition tolerance is non-negotiable
- [ ] Availability and Partition tolerance (sacrifice consistency is never acceptable)
- [ ] None — CAP theorem only applies to databases, not file systems

**Q4. What problem do "fencing tokens" solve in distributed lock services?**

- [ ] They prevent two clients from acquiring the same lock simultaneously in normal operation
- [ ] They encrypt lock requests to prevent eavesdropping on the lock service
- [x] They prevent a slow lock holder (whose lock expired) from completing a write after a newer holder has already taken over, by rejecting writes with a stale token
- [ ] They ensure locks are always granted in FIFO order to prevent starvation

**Q5. MCS locks improve multi-core spinlock performance by:**

- [ ] Using a centralized kernel thread to serialize all lock acquisitions
- [ ] Replacing busy-waiting with a sleep-and-wake mechanism like a mutex
- [x] Having each waiting thread spin on its own private cache-coherent node, eliminating the thundering-herd cache invalidation that occurs when all threads spin on the same location
- [ ] Automatically upgrading to a read-write lock when multiple threads want read-only access

**Q6. Dynamic Voltage and Frequency Scaling (DVFS) reduces power consumption by:**

- [ ] Migrating processes to idle cores to consolidate heat generation
- [ ] Turning off CPU caches when the system is underloaded
- [x] Lowering the CPU's clock frequency and supply voltage when utilization is low, since power scales roughly with V^2 * f
- [ ] Suspending all background processes to DRAM during low-utilization periods
