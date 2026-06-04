# Quiz: Persistence and Replication

Test your knowledge of RDB, AOF, Redis Replication, and Sentinel.

## Question 1

With `appendfsync everysec`, how much data can you lose at most if Redis crashes?

[ ] Zero — every write is fsynced immediately
[x] Up to 1 second of writes
[ ] Up to 1 minute of writes
[ ] All data since the last RDB snapshot

## Question 2

You want the fastest Redis restart time after a crash with minimal data loss. Which configuration gives the best balance?

[ ] AOF only with `appendfsync always`
[ ] RDB only with a 60-second save interval
[x] RDB + AOF hybrid mode (`aof-use-rdb-preamble yes`)
[ ] No persistence — rebuild from the primary database

## Question 3

Which statement about RDB snapshots is CORRECT?

[ ] RDB logs every write command in text format
[x] RDB creates a binary point-in-time dump using a forked child process
[ ] RDB uses `appendfsync` to control durability
[ ] RDB is incompatible with AOF and cannot be used together

## Question 4

Redis Sentinel provides which capability?

[ ] Horizontal sharding of keys across multiple nodes
[ ] Blocking the primary from accepting writes during a replica lag
[x] Automatic failover: promoting a replica to primary when the primary fails
[ ] Compressing AOF files to reduce disk usage

## Question 5

What is the main reason to use `appendfsync no` instead of `appendfsync everysec`?

[x] Maximum write throughput when durability is not required (OS decides when to flush)
[ ] Guaranteed zero data loss
[ ] Compatibility with Redis Cluster
[ ] Reducing CPU usage during AOF rewrite

## Question 6

A developer disables persistence entirely on a Redis instance used only as a cache. What command in `redis.conf` disables RDB snapshots?

[ ] `appendonly no`
[ ] `rdb-del-sync-files yes`
[x] `save ""`
[ ] `maxmemory-policy noeviction`

## Question 7

Redis replication is asynchronous. What does this mean in practice?

[x] A replica may lag behind the primary, so reads from a replica can return stale data
[ ] Writes to the primary block until all replicas confirm receipt
[ ] Replicas automatically become primaries if they detect the primary is slow
[ ] AOF must be enabled on both primary and replica for replication to work

## Question 8

Redis Cluster uses hash slots to distribute keys. How many total hash slots does a Redis Cluster have?

[ ] 1,024
[ ] 4,096
[ ] 65,536
[x] 16,384
