# Build a Leaderboard

Simulate Redis sorted-set commands in Python. Read a sequence of commands like:

```
ZADD alice 10
ZADD bob 20
ZINCRBY alice 5
ZTOP 3
```

After each `ZTOP K`, print the top K members in score-descending order (alphabetical for ties).

See the prompt for the precise I/O.
