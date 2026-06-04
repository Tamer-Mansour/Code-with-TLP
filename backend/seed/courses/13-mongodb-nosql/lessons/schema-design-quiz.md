# Quiz — Schema Design and Data Modeling

Test your understanding of MongoDB schema design patterns and the embed vs reference decision.

---

**Question 1:** You are modeling a blog where each post has many comments, and users can write thousands of comments over time. Which approach is BEST?

[ ] Embed all comments inside the post document
[ ] Embed all comments inside the user document
[x] Store comments in a separate collection and reference the post and user by ID
[ ] Use a single flat collection with one document per comment containing the full post text

---

**Question 2:** What is the maximum document size in MongoDB?

[ ] 1 MB
[x] 16 MB
[ ] 64 MB
[ ] 256 MB

---

**Question 3:** The "Bucket Pattern" is best suited for which use case?

[ ] Storing user profiles with variable attributes
[x] Time-series data where grouping many events into one document reduces document count
[ ] Sharing a single category document across many products
[ ] Migrating a relational schema to MongoDB

---

**Question 4:** MISCONCEPTION CHECK — Which statement is TRUE about MongoDB's schema?

[ ] MongoDB is schema-less; you can never enforce required fields
[ ] MongoDB enforces a strict schema like SQL for all collections
[x] MongoDB has a flexible schema by default, but you can opt into validation using `$jsonSchema`
[ ] Schema validation in MongoDB requires a paid Atlas subscription

---

**Question 5:** The "Computed Pattern" involves:

[ ] Using `$unwind` to flatten arrays before grouping
[x] Caching aggregated values (like totals or counts) directly in the parent document, updated on each write
[ ] Splitting large documents into smaller ones automatically
[ ] Embedding computed indexes inside each document

---

**Question 6:** When should you choose **referencing** over **embedding**?

[ ] When children are always read together with the parent
[ ] When children are bounded (at most 5–10 per parent)
[x] When children are unbounded, shared across parents, or have an independent lifecycle
[ ] When you need the highest write throughput

---

**Question 7:** The "Subset Pattern" means:

[ ] Indexing only a subset of documents using a partial index
[ ] Storing only some fields from each document
[x] Embedding the most recent or most relevant N children while referencing the full list
[ ] Partitioning a collection into multiple smaller collections

---

**Question 8:** Which of the following is an anti-pattern in MongoDB schema design?

[ ] Embedding a small, fixed set of related items
[ ] Using references for high-traffic shared lookup data
[x] Storing an ever-growing array inside a document (e.g., pushing every event to an array field)
[ ] Validating documents with `$jsonSchema`
