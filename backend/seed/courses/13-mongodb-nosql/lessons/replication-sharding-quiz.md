# Quiz — Replication, Sharding, and Distributed Operations

Test your understanding of MongoDB's high-availability and horizontal scaling mechanisms.

---

**Question 1:** In a MongoDB replica set, which node accepts all write operations?

[ ] Any node with the lowest latency
[ ] The secondary with the most up-to-date oplog
[x] The primary node
[ ] The arbiter node

---

**Question 2:** What is the purpose of the **oplog** in a MongoDB replica set?

[ ] It stores failed write operations for retry
[ ] It is the query explain output log
[x] It is a capped collection on the primary that records every write, allowing secondaries to replicate changes
[ ] It stores slow query logs captured by the profiler

---

**Question 3:** You use `w: "majority"` write concern. What does this guarantee?

[ ] The write was written to at least one secondary
[ ] The write was written to all members of the replica set
[x] The write was acknowledged by more than half the voting members before returning success
[ ] The write was flushed to disk on the primary only

---

**Question 4:** When reading from a secondary with `readPreference: "secondary"`, what consistency tradeoff do you accept?

[ ] Writes may fail with higher frequency
[ ] You cannot use aggregation pipelines
[x] Reads may return slightly stale data due to replication lag
[ ] You cannot read documents larger than 1 MB

---

**Question 5:** In a sharded MongoDB cluster, what is the role of **mongos**?

[ ] It stores the actual document data
[ ] It manages replica set elections
[x] It is the query router that receives client requests and routes them to the correct shard(s)
[ ] It holds the config server metadata

---

**Question 6:** MISCONCEPTION CHECK — Why is an auto-incrementing integer a bad shard key for write-heavy workloads?

[ ] MongoDB does not support integer shard keys
[ ] It creates too many chunks for the balancer to manage
[x] New documents always land on the same shard (the one holding the highest range), creating a write hotspot
[ ] It prevents targeted queries

---

**Question 7:** What is a "scatter-gather" query in MongoDB sharding?

[ ] A query that uses `$lookup` across multiple collections
[x] A query without a shard key filter, which must be sent to every shard and results merged
[ ] A `$facet` pipeline that runs multiple sub-pipelines
[ ] A query that uses TTL indexes to expire old data

---

**Question 8:** Which `readPreference` should you use to guarantee reading your own most recent writes?

[x] `primary`
[ ] `secondary`
[ ] `nearest`
[ ] `secondaryPreferred`
