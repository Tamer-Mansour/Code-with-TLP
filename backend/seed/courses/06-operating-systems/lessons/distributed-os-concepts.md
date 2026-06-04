# Distributed Systems and OS Support

When multiple machines work together — whether as a distributed file system, a cloud cluster, or a networked application — the OS must provide mechanisms for coordinated access, transparent naming, and fault tolerance. This lesson covers the OS-level concepts underpinning distributed systems.

## Remote Procedure Call (RPC)

**RPC** makes a function call to code on a remote machine look like a local call. The programmer writes:

```python
result = remote_server.compute_sum(42, 58)  # looks local
```

Underneath, a **stub** (generated code) marshals the arguments into a message, sends it over the network, waits for a reply, and unmarshals the result. The server has a matching stub that unpacks arguments and calls the real function.

### RPC Semantics

What happens if the network drops the request or the server crashes mid-call?

| Semantics | Guarantee | Use Case |
|-----------|-----------|----------|
| **At-most-once** | Server executes the call 0 or 1 times | Idempotent operations, payment processing |
| **At-least-once** | Server executes the call ≥1 times (retried until ACK) | Read-only operations, DNS lookups |
| **Exactly-once** | Server executes exactly once (requires two-phase commit) | Distributed transactions |

Achieving exactly-once semantics in the presence of network partitions requires consensus protocols like Paxos or Raft — expensive but necessary for databases.

## Distributed File Systems

### NFS (Network File System)

Sun's NFS (1984, NFSv4 current) exposes a file system over the network using a **stateless design**:

- The server stores no session state between requests. Every RPC carries enough context to be processed independently.
- A client crash and reconnect is transparent — just retry the last request.
- Downside: some operations are hard to make idempotent (e.g., `mkdir` — creating a directory twice fails the second time).

```
NFS Architecture:
Client Machine          Server Machine
─────────────           ──────────────
App calls open()        
  └─► VFS layer         
      └─► NFS client    ─── MOUNT RPC ──► Server exports /data
          └─► RPC calls ─── LOOKUP RPC ──► Returns file handle
                         ─── READ RPC ──► Returns bytes
```

**File handles** (not path names) identify files. A file handle is an opaque identifier including the filesystem ID, inode number, and generation counter. Stable across server reboots.

### AFS (Andrew File System)

Carnegie Mellon's AFS uses **callback-based caching** — a fundamentally different consistency model:

1. Client fetches a file and caches it locally
2. Server records a **callback promise**: "I will notify you if this file changes"
3. Client reads/writes the local cached copy (fast, no network round-trips)
4. If another client modifies the file, the server **breaks** the first client's callback
5. On next access, the invalidated client fetches the new version

AFS scales better than NFS for **read-mostly** workloads (documents, source code) because repeated reads hit the local cache after the first fetch. NFS checks the server on every open by default.

## Consistency Models in Distributed Storage

How "fresh" must a read be relative to the latest write?

| Model | Guarantee | Example System |
|-------|-----------|----------------|
| **Strict/Linearizability** | Every read sees the most recent write, globally ordered | Single-node RDBMS |
| **Sequential consistency** | All nodes see writes in the same order (not necessarily real-time) | Zookeeper |
| **Causal consistency** | Writes that are causally related appear in causal order | CockroachDB |
| **Eventual consistency** | All replicas converge given no new writes | Amazon DynamoDB, Cassandra |

The **CAP theorem** (Brewer, 2000): a distributed system can guarantee at most two of: Consistency, Availability, Partition tolerance. Since network partitions are unavoidable, real systems choose between CP (consistent but may be unavailable during partition) and AP (always available, may return stale data).

## Distributed Locking

When multiple nodes need exclusive access to a shared resource (a file, a database record, a configuration key), a **distributed lock service** coordinates access:

```
Client A                Lock Service (Chubby/ZooKeeper)          Client B
────────                ─────────────────────────────             ────────
ACQUIRE lock_key ──►  Grant lock, set TTL=30s               
  (holds lock)                                          ACQUIRE lock_key ──► WAIT (blocked)
UPDATE shared_state
RELEASE lock_key ──►  Release; notify Client B
                                                        Grant lock to B
```

**Fencing tokens**: to handle the case where a client holds a lock but is then slow (GC pause, network jitter) and the lock expires before it finishes, the lock service returns a monotonically-increasing **fencing token** with each grant. Storage backends reject writes with a token older than the latest one seen.

## Scalable Locking in Multi-Core Systems

Even on a single machine, a simple spinlock becomes a bottleneck when many cores compete:

### MCS Lock (Mellor-Crummey and Scott, 1991)

Each waiting thread spins on its **own** cache-coherent node in a per-CPU linked list, rather than all spinning on the same memory location. This eliminates the cache thrashing where every lock release causes all waiting cores to invalidate and re-fetch the same cache line:

```
Lock holder → Node A → Node B → Node C (tail)
              ↑                   ↑
         current lock holder   last queued thread
         
Each thread spins on its own node.prev_granted field — no shared memory contention.
```

MCS locks reduce cache-line invalidations from O(N) to O(1) on every acquire, making them the standard for high-contention kernel locks.

## Energy and Power Management

Modern CPUs support **Dynamic Voltage and Frequency Scaling (DVFS)**: the OS can reduce CPU frequency (and voltage) to save power when utilization is low.

```bash
# Linux cpufreq — view and set CPU frequency policy
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# powersave    ← run at minimum frequency always
# performance  ← run at maximum frequency always
# ondemand     ← scale frequency based on utilization
# schedutil    ← CFS-integrated governor (used in modern kernels)

# Force all CPUs to powersave mode:
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

The **P-state** (performance state) determines frequency/voltage pairs:

```
P0: 3.6 GHz, 1.2V    (max performance, max power)
P1: 2.8 GHz, 1.0V
P2: 2.0 GHz, 0.9V
P3: 1.2 GHz, 0.8V    (power saving)
```

On mobile and embedded systems, aggressive DVFS (and clock gating — turning off unused subsystems entirely) is the primary battery-life optimization. The Linux kernel's `schedutil` governor integrates DVFS decisions directly with the CFS scheduler's load estimates.

## Key Takeaways

- **RPC** provides location transparency for remote calls; semantics (at-most-once vs. at-least-once vs. exactly-once) determine fault tolerance guarantees.
- **NFS** is stateless (each RPC self-contained); **AFS** uses callback-based caching for better read scalability.
- **Consistency models** (linearizable → eventual) trade correctness for availability; the CAP theorem quantifies the fundamental trade-off.
- **Distributed locks** require fencing tokens to handle slow-lock holders whose lock expired before they finished.
- **MCS locks** eliminate cache-line thrashing on multi-core systems by giving each waiter its own spin location.
- **DVFS** lets the OS dynamically reduce CPU frequency/voltage to save power, integrated into the scheduler via governors like `schedutil`.

## Further Reading

- OSTEP Chapter 49 — Distributed Systems (Introduction): https://pages.cs.wisc.edu/~remzi/OSTEP/
- OSTEP Chapter 50 — Sun's Network File System (NFS): https://pages.cs.wisc.edu/~remzi/OSTEP/
- OSTEP Chapter 51 — The Andrew File System (AFS): https://pages.cs.wisc.edu/~remzi/OSTEP/
- MIT 6.828 readings on scalable locking: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/
