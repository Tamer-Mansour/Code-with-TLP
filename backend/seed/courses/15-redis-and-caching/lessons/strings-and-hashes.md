# Strings and Hashes

## Strings

The simplest type. Despite the name, a Redis "string" holds any binary up to 512 MB — text, JSON, an image, a serialized object.

```
SET   user:42:name "Alice"
GET   user:42:name
APPEND user:42:name " Adams"
STRLEN user:42:name
```

### As integers

```
SET counter 0
INCR counter         -> 1
INCR counter         -> 2
INCRBY counter 10    -> 12
DECR counter         -> 11
```

Atomic increment is the basis of rate limiters, counters, ID generators.

### As bitmaps

A string can be addressed bit-by-bit:

```
SETBIT online:2025-06-01 42 1
GETBIT online:2025-06-01 42
BITCOUNT online:2025-06-01
```

8 million users tracked per day = 1 MB. Fast set membership without a Set.

### Options on SET

```
SET key val EX 60          # expire in 60 seconds
SET key val PX 5000        # expire in 5000 milliseconds
SET key val NX             # only if NOT exists  (distributed lock primitive)
SET key val XX             # only if exists
SET key val EX 30 NX       # combine
GETSET key newval          # set, return old
SETNX key val              # set-if-not-exists (legacy form)
```

## Hashes

A hash is a map of string fields to string values under a single key — like a tiny object.

```
HSET   user:42 name "Alice" email "alice@x.com" age 30
HGET   user:42 email
HGETALL user:42
HMGET  user:42 name age
HINCRBY user:42 loginCount 1
HDEL   user:42 age
HEXISTS user:42 name
HLEN   user:42
```

### Why hashes vs many strings?

Comparing two approaches to "store user profile":

**Strings:**
```
SET user:42:name  "Alice"
SET user:42:email "alice@x.com"
SET user:42:age   30
```

**Hash:**
```
HSET user:42 name "Alice" email "alice@x.com" age 30
```

The hash uses dramatically less memory for small objects (Redis uses a compact `listpack` encoding under a threshold), and groups related fields under one key for easier expiry / deletion.

### When NOT to use one big hash

- If individual fields are large (kilobytes+), the compact encoding flips to a hashtable — bigger.
- If you need TTL on individual fields, you can't — TTL is per key. (HEXPIRE landed in 7.4 — see release notes if you need it.)

## Naming convention

The community has settled on **colon-delimited keys** that describe the shape:

```
user:42                  # hash of user 42's fields
user:42:friends          # set of friend IDs
session:abc123           # string blob, TTL 3600
rate:user:42:1h          # counter expiring in 1h
```

Consistency makes `SCAN MATCH "user:*"` and operational tools work.
