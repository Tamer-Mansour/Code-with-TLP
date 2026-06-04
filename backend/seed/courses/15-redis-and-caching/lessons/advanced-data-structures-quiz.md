# Quiz: Advanced Data Structures

Test your understanding of HyperLogLog, Sorted Sets, Streams, and probabilistic data structures in Redis.

## Question 1

What is the maximum memory used by a single Redis HyperLogLog key, regardless of how many unique elements have been added?

[ ] 1 KB
[ ] 64 KB
[x] 12 KB
[ ] It grows with the number of elements

## Question 2

You need to track unique visitor counts per day for 10 million users. Which data structure gives the lowest memory footprint if an approximate count (within 1%) is acceptable?

[ ] Redis Set
[ ] Redis Sorted Set
[x] HyperLogLog
[ ] Redis Hash

## Question 3

Redis Sorted Set members with the same score are ordered by which tiebreaker?

[x] Lexicographic order of the member string
[ ] Insertion time (FIFO)
[ ] Random order
[ ] The order is undefined

## Question 4

Which command returns the rank of a member in a Sorted Set from highest to lowest score?

[ ] ZRANK
[x] ZREVRANK
[ ] ZSCORE
[ ] ZREVRANGE

## Question 5

A developer uses Redis Pub/Sub to notify microservices when a cache key is invalidated. A subscriber is temporarily offline for 2 minutes. What happens to the messages published during that time?

[x] They are lost — Pub/Sub has no message persistence
[ ] They are buffered and delivered when the subscriber reconnects
[ ] They are replayed from the AOF log
[ ] They are stored in a dead-letter queue

## Question 6

You want to implement a priority queue where tasks are dequeued in order of urgency (lowest number = highest priority). Which data structure and command is the best fit?

[ ] List with LPUSH / RPOP
[x] Sorted Set with ZADD (score = priority) and ZPOPMIN
[ ] Set with SADD / SPOP
[ ] Hash with HSET / HGETALL

## Question 7

Redis Streams differ from Pub/Sub in which critical way?

[ ] Streams support multiple data types; Pub/Sub only supports strings
[ ] Streams require a cluster; Pub/Sub works on a single node
[x] Streams persist messages to disk and support consumer groups with acknowledgment
[ ] Streams are faster than Pub/Sub for high-throughput workloads

## Question 8

`PFMERGE` combines two HyperLogLog structures. What does the result represent?

[ ] The intersection of the two sets
[x] An estimate of the union (distinct elements seen in either HLL)
[ ] The sum of the two cardinality estimates
[ ] The larger of the two cardinality values
