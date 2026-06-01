# find, Filters, and Projection

`db.coll.find(query, projection)` is your `SELECT`. Both arguments are objects.

## Basic queries

```javascript
db.users.find({});                          // all
db.users.find({ name: "Alice" });           // exact match
db.users.find({ age: { $gte: 18 } });       // operator
db.users.findOne({ _id: ObjectId("...") }); // single doc
```

## Comparison operators

| Operator | Meaning             |
|----------|---------------------|
| `$eq`    | equals              |
| `$ne`    | not equals          |
| `$gt`    | greater than        |
| `$gte`   | greater or equal    |
| `$lt`    | less than           |
| `$lte`   | less or equal       |
| `$in`    | value in array      |
| `$nin`   | value not in array  |

```javascript
db.orders.find({ status: { $in: ["paid", "shipped"] } });
db.orders.find({ total: { $gt: 100, $lt: 500 } });
```

## Logical operators

```javascript
db.users.find({
  $or: [
    { isAdmin: true },
    { loginCount: { $gte: 100 } }
  ]
});

db.users.find({
  $and: [
    { country: "DE" },
    { age: { $gte: 18 } }
  ]
});
```

Implicit `$and` — you can usually skip it: `{ country: "DE", age: { $gte: 18 } }`.

## Array operators

```javascript
db.users.find({ tags: "admin" });                   // any document where tags contains "admin"
db.users.find({ tags: { $all: ["admin","early"] } });
db.users.find({ tags: { $size: 3 } });
db.users.find({ "items.sku": "A" });                // any item with sku A (dot notation)
```

## Nested fields

```javascript
db.orders.find({ "address.country": "DE" });
db.orders.find({ "items.price": { $gt: 10 } });
```

## Projection — picking fields

Second argument: `1` to include, `0` to exclude. Mixing is only allowed for `_id`.

```javascript
db.users.find({}, { name: 1, email: 1 });             // only name + email + _id
db.users.find({}, { name: 1, _id: 0 });               // name, no _id
db.users.find({}, { password: 0 });                   // everything except password
```

## Sorting, limiting, skipping

```javascript
db.orders
  .find({ status: "paid" })
  .sort({ createdAt: -1 })
  .skip(20)
  .limit(10);
```

`1` for ascending, `-1` for descending. Always `sort` before `limit` to get the rows you expect.

## Cursors and counts

```javascript
const c = db.orders.find({ status: "paid" });
c.hasNext();
c.next();

db.orders.countDocuments({ status: "paid" });   // exact, slower
db.orders.estimatedDocumentCount();             // fast, from metadata
```

## Regex search

```javascript
db.users.find({ email: /@example\.com$/i });
```

Anchored regexes (`/^foo/`) can use an index; unanchored ones cannot.
