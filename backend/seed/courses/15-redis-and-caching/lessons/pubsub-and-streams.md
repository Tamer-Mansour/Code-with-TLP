# Pub/Sub and Streams

Two messaging primitives in Redis. They look similar; they're very different.

## Pub/Sub — fire-and-forget

```
> SUBSCRIBE chat
> PUBLISH chat "hello"
```

Subscribers receive every message published while they're connected. There is **no persistence** — if you weren't listening, the message is gone.

Subscribe to many channels:

```
SUBSCRIBE chat:1 chat:2
PSUBSCRIBE chat:*       # pattern subscription
```

Use when:
- Messages are ephemeral (live cursor updates, presence, cache invalidation broadcasts).
- All subscribers see all messages.
- You don't care about replaying history.

### Don't use Pub/Sub for jobs

It's not durable. A subscriber crash drops in-flight messages. For "exactly-once-ish" work queues, use Streams.

### Keyspace notifications

A built-in pub/sub feed of key events ("key X was set / deleted / expired"). Enable with `notify-keyspace-events`. Useful for triggering callbacks when keys expire.

## Streams — append-only log with consumer groups

`XADD` appends an entry. `XREAD` / `XREADGROUP` reads from any position with acknowledgement. This is Kafka, scaled down to Redis.

```
> XADD events * type login user 42
"1717000000000-0"

> XADD events * type purchase user 42 amount 99
"1717000000001-0"

> XLEN events
> XRANGE events - +              # all entries
```

Each entry gets a monotonically increasing ID (`millis-seq`). You can specify your own.

### Consumer groups

A group of workers, each reading a subset and acknowledging completion.

```
> XGROUP CREATE events workers $ MKSTREAM
> XREADGROUP GROUP workers worker-1 COUNT 10 BLOCK 5000 STREAMS events >
... process messages ...
> XACK events workers 1717000000000-0
```

The `>` says "give me messages no consumer in this group has seen". `XACK` removes the entry from the pending list for that consumer.

### Reliability features

- **Pending Entry List (PEL)** — entries delivered to a consumer but not yet acked. Survive consumer restarts.
- `XPENDING` and `XCLAIM` — inspect and reassign messages from a dead consumer to a healthy one.
- **Capped streams** — `XADD events MAXLEN ~ 1000000 * ...` keeps only the most recent ~1M entries.

### When to use Streams

- Reliable work queues (instead of `LPUSH`/`BRPOP`).
- Event sourcing within a single application.
- Inter-service messaging when Kafka is overkill.

### When not to

- Throughput in the millions/sec across many topics → Kafka.
- Cross-region replication beyond what Redis offers natively.
- Long retention (Streams are in-RAM; you pay).

## A quick comparison

| Need                                       | Pub/Sub | Streams | List (LPUSH/BRPOP) |
|--------------------------------------------|:------:|:------:|:----:|
| Live broadcast, no replay                  |  ✓     |        |      |
| Durable queue with ack and retries         |        |  ✓     |  ⚠️   |
| Fan-out to many consumers, each their own  |        |  ✓     |      |
| Tiny in-process FIFO                       |        |        |  ✓   |

Streams are the modern answer for most queue-shaped problems Redis is asked to solve.
