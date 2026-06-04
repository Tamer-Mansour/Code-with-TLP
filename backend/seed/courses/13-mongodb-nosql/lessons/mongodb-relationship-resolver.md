# Embedded vs Referenced Relationship Resolver

One of the fundamental schema design decisions in MongoDB is whether to **embed** related data inside a document or **reference** it by storing an ID (like a foreign key). This exercise simulates the reference model: users and orders live in separate "collections" and you resolve the relationship programmatically.

## The Exercise

Given a list of users and a list of orders (where each order references a user by ID), print a summary for each user: how many orders they placed and their total order amount.

This mirrors what a `$lookup` aggregation stage does in MongoDB — joining orders to users by a shared field.

## Example

Input:

```
3
u1:Alice
u2:Bob
u3:Carol
4
o1:u1:100
o2:u2:200
o3:u1:150
o4:u2:50
```

Output:

```
Alice: 2 orders, total: 250
Bob: 2 orders, total: 250
Carol: 0 orders, total: 0
```

## Embed vs Reference: The Trade-Off

### Embed

Store orders inside the user document:

```json
{
  "_id": "u1",
  "name": "Alice",
  "orders": [
    { "orderId": "o1", "amount": 100 },
    { "orderId": "o3", "amount": 150 }
  ]
}
```

**Pros:** One read returns all data. Atomic updates across user + orders.

**Cons:** Document grows unbounded if a user places thousands of orders. Hitting the 16 MB document limit is a real risk.

### Reference

Store orders in a separate collection:

```json
// users collection
{ "_id": "u1", "name": "Alice" }

// orders collection
{ "_id": "o1", "userId": "u1", "amount": 100 }
{ "_id": "o3", "userId": "u1", "amount": 150 }
```

**Pros:** Documents stay small. Orders have their own lifecycle (cancellation, archiving). No 16 MB risk.

**Cons:** Two queries to assemble a full view. `$lookup` adds pipeline overhead.

## Resolving References with $lookup

The MongoDB equivalent of this exercise:

```javascript
db.users.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "userId",
      as: "userOrders"
    }
  },
  {
    $project: {
      name: 1,
      orderCount: { $size: "$userOrders" },
      total: { $sum: "$userOrders.amount" }
    }
  }
]);
```

This is exactly the computation the exercise asks you to do in Python.

## Decision Rules for Embed vs Reference

| Situation | Choose |
|-----------|--------|
| Child records are bounded (e.g., at most 10 items per order) | Embed |
| Child records are unbounded (e.g., user activity log) | Reference |
| You always read parent + children together | Embed |
| Children have independent lifecycle (can be deleted/transferred) | Reference |
| Children are shared across multiple parents (tags, categories) | Reference |
| You need atomic writes across parent and children | Embed (or transaction) |

## The Subset Pattern

A common hybrid: embed the *most recent* or *most relevant* N children, reference the rest.

```json
{
  "_id": "u1",
  "name": "Alice",
  "recentOrders": [ { "orderId": "o3", "amount": 150 } ],
  "totalOrderCount": 2
}
```

Renders quickly for the common case (show last order); loads the full list on demand with a second query.

## Further Reading

- Martin Fowler and Pramod Sadalage, *NoSQL Distilled — Chapter 13: Polyglot Persistence* (free sample): [https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_NoSQL_Ch_13_en.pdf](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_NoSQL_Ch_13_en.pdf)
- Martin Fowler, *Introduction to NoSQL* (YouTube, 54 min): [https://www.youtube.com/watch?v=qI_g07C_Q5I](https://www.youtube.com/watch?v=qI_g07C_Q5I) — covers aggregate-oriented design and the embed vs reference decision.
