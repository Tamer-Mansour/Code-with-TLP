# Quiz — Indexes and Query Performance

Test your understanding of MongoDB indexing concepts.

---

**Question 1:** What does the ESR rule stand for when building compound indexes?

[ ] Elements, Sorting, Ranges
[ ] Equality, Sequential, Ranking
[x] Equality, Sort, Range
[ ] Exact, Selective, Ranked

---

**Question 2:** You create the compound index `{ status: 1, customer: 1, createdAt: -1 }`. Which query CANNOT use this index efficiently due to the leftmost-prefix rule?

[ ] `find({ status: "paid" })`
[ ] `find({ status: "paid", customer: "alice" })`
[x] `find({ customer: "alice" })`
[ ] `find({ status: "paid", customer: "alice", createdAt: { $gte: d } })`

---

**Question 3:** What is a "covered query" in MongoDB?

[ ] A query that runs inside a transaction
[ ] A query that uses `$text` full-text search
[x] A query where all requested fields are in the index, so no document fetch is needed
[ ] A query with a `hint()` forcing a specific index

---

**Question 4:** Which index type automatically removes documents after a set time period?

[ ] Hashed index
[ ] Sparse index
[x] TTL (Time-To-Live) index
[ ] Wildcard index

---

**Question 5:** An index on a `status` field with only two possible values (`active`, `inactive`) is considered:

[ ] High selectivity — good for most queries
[x] Low selectivity — the index may be skipped by the query planner
[ ] A partial index — it only indexes some documents
[ ] A multikey index — it indexes array values

---

**Question 6:** What does `explain("executionStats")` report that helps you identify a missing index?

[ ] The number of collections in the database
[x] `totalDocsExamined` vs `nReturned` — a high ratio indicates a collection scan
[ ] The size of each document in the result set
[ ] Whether the query used a transaction

---

**Question 7:** MISCONCEPTION CHECK — Which statement is TRUE about MongoDB indexes?

[ ] Every index you create always speeds up both reads and writes
[ ] You should index every field that appears in any query
[x] Indexes slow down writes slightly and consume RAM, so only index fields on hot query paths
[ ] MongoDB automatically creates indexes for all fields you query frequently

---

**Question 8:** Which of the following is a valid use case for a **hashed index** in MongoDB?

[ ] Range queries like `{ age: { $gte: 18 } }`
[ ] Sorting documents by creation time
[x] Distributing documents evenly across shards in a sharded cluster
[ ] Full-text search on string fields
