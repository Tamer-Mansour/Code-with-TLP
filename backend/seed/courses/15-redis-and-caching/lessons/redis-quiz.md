# Quiz: Redis Basics

**Q1. Redis stores all its data primarily in:**
- [ ] Disk (B-tree)
- [x] RAM
- [ ] Object storage (S3)
- [ ] An LSM tree on disk

**Q2. The default Redis port is:**
- [ ] 3306
- [ ] 5432
- [x] 6379
- [ ] 27017

**Q3. Which command should you NOT run in a large production Redis?**
- [ ] `GET`
- [x] `KEYS *`
- [ ] `SCAN`
- [ ] `SET`

**Q4. Redis command processing is:**
- [ ] Multi-threaded by default
- [x] Single-threaded for commands (multi-threaded for I/O in 6+)
- [ ] One thread per connection
- [ ] Fork-per-command

**Q5. Which data type would you use for a leaderboard?**
- [ ] String
- [ ] Hash
- [ ] List
- [x] Sorted set (ZSET)

**Q6. To make a key automatically expire after 60 seconds you can use:**
- [ ] `SET key val TTL 60`
- [x] `SET key val EX 60`
- [ ] `SET key val EXPIRE 60`
- [ ] `EXPIRE_IN key 60`
