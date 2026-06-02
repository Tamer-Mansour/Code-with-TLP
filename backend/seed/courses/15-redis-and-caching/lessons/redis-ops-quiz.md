# Quiz: Redis Operations and Persistence

**Q1. Which command gives you a real-time stream of every command being processed by Redis?**
- [ ] `DEBUG SLEEP`
- [ ] `SLOWLOG GET`
- [x] `MONITOR`
- [ ] `INFO stats`

**Q2. You set `maxmemory-policy allkeys-lru`. What happens when Redis runs out of memory?**
- [ ] Redis stops accepting all commands.
- [x] Redis evicts the least-recently-used key from any key (with or without TTL).
- [ ] Redis evicts only keys that have a TTL set.
- [ ] Redis crashes with an out-of-memory error.

**Q3. A hash with 50 fields where every value is under 64 bytes will use which internal encoding?**
- [ ] `hashtable`
- [x] `ziplist` or `listpack`
- [ ] `skiplist`
- [ ] `quicklist`

**Q4. You need to count distinct user IDs that visited a page today. You expect ~10 million unique visitors and can tolerate a 1% error. Which data structure is most memory-efficient?**
- [ ] Redis Set
- [ ] Redis List
- [x] HyperLogLog
- [ ] Sorted Set

**Q5. RDB snapshots are configured with `save 900 1`. What does this mean?**
- [x] Save a snapshot if at least 1 key changed in the last 900 seconds.
- [ ] Save a snapshot every 900 milliseconds.
- [ ] Save the last 900 writes to disk.
- [ ] Take 1 snapshot per 900 commands.

**Q6. In a Redis Sentinel setup, what is the minimum number of Sentinel instances recommended for a reliable quorum?**
- [ ] 1
- [ ] 2
- [x] 3
- [ ] 5

**Q7. What is the purpose of the `WAIT` command in Redis replication?**
- [ ] It pauses all reads until a replica connects.
- [x] It blocks the client until a specified number of replicas have acknowledged the latest write.
- [ ] It waits for an AOF `fsync` to complete.
- [ ] It delays command execution by a given number of milliseconds.

**Q8. Which eviction policy should you use when Redis is a primary store (not a cache) and you want writes to fail rather than lose data?**
- [ ] `allkeys-lru`
- [ ] `volatile-lru`
- [x] `noeviction`
- [ ] `allkeys-random`
