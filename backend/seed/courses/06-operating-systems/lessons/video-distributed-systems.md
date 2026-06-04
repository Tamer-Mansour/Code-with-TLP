# Video: Distributed Systems and OS Scalability

This video unit covers how operating systems support distributed computing — from remote procedure calls and distributed file systems to multi-core scalability and power management.

## What You Will Learn

- Remote Procedure Call (RPC) semantics: at-most-once, at-least-once, exactly-once
- NFS (stateless design) vs. AFS (callback-based caching)
- Consistency models: linearizability, sequential consistency, eventual consistency
- The CAP theorem and the CP vs. AP trade-off
- Distributed lock services (Chubby, ZooKeeper) and fencing tokens
- Scalable multi-core locking: MCS locks and cache-line considerations
- CPU frequency scaling (DVFS) and Linux cpufreq governors

## Recommended Resource

Search YouTube for "distributed systems Martin Kleppmann" (his lectures from Cambridge) or "NFS vs AFS distributed file systems". For scalable locking, "MCS lock explained" has good visualizations.

## Reference Material

- OSTEP Chapters 49–51 — Distributed Systems, NFS, AFS: https://pages.cs.wisc.edu/~remzi/OSTEP/
- MIT 6.828 scalable locking readings: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/
