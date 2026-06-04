# Quiz: Pub/Sub, Streams, and Cluster

Verify your understanding of Redis messaging primitives and horizontal scaling.

## Question 1

A subscriber to a Redis Pub/Sub channel is offline for 10 minutes. When it reconnects, what happens to messages published during those 10 minutes?

[x] The messages are permanently lost — Pub/Sub is fire-and-forget
[ ] Redis buffers up to 1,000 messages per subscriber
[ ] The messages are replayed from the AOF log
[ ] The subscriber receives the messages via a delivery retry queue

## Question 2

Which Redis data structure supports consumer groups, message acknowledgment, and replay from a specific message ID?

[ ] List
[ ] Pub/Sub channel
[x] Stream
[ ] Sorted Set

## Question 3

Redis Cluster shards keys across nodes using hash slots. When a client requests a key that lives on a different node than the one it connected to, what does that node respond with?

[ ] It proxies the request transparently to the correct node
[x] It returns a MOVED redirect pointing to the correct node
[ ] It returns an error and closes the connection
[ ] It fetches the key from the correct node and caches it locally

## Question 4

A single Redis Cluster key is receiving 5 million requests per second — far beyond what one node can handle. Why does adding more cluster nodes NOT solve this?

[ ] Redis Cluster cannot exceed 16,384 nodes
[ ] The key would need to be manually migrated to a new node
[x] A single key always maps to one hash slot on one node; sharding does not distribute load for a single key
[ ] Redis Cluster only distributes writes, not reads

## Question 5

You need to build a reliable task queue where workers acknowledge task completion and unprocessed tasks are retried if a worker dies. Which Redis data structure should you use?

[ ] List with BRPOP
[ ] Pub/Sub channel
[x] Stream with consumer groups (XREADGROUP / XACK)
[ ] Sorted Set with ZPOPMIN

## Question 6

`SUBSCRIBE news sports` registers a client on two channels. If 3 messages are published to `news` and 2 to `sports`, how many messages does the subscriber receive?

[x] 5
[ ] 2 (only the most recent per channel)
[ ] 3 (only `news`, the first subscribed channel)
[ ] It depends on the subscriber's connection speed

## Question 7

Which command reads new messages from a Redis Stream without consumer groups, starting from where you last left off?

[ ] SUBSCRIBE stream-key
[ ] BRPOP stream-key 0
[x] XREAD COUNT 10 BLOCK 0 STREAMS stream-key $
[ ] LRANGE stream-key 0 -1

## Question 8

Redis Cluster's `CLUSTER KEYSLOT key` returns a number between 0 and 16383. What is this number used for?

[ ] The index of the primary node that owns the key
[x] The hash slot, which determines which node in the cluster stores the key
[ ] The TTL in milliseconds for the key
[ ] The position of the key in the node's sorted keyspace
