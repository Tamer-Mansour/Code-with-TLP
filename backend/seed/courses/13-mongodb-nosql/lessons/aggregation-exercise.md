# Simulate a $group + $sort Pipeline

Time to mimic this pipeline in Python:

```javascript
db.sales.aggregate([
  { $group: { _id: "$category", total: { $sum: "$amount" } } },
  { $sort:  { total: -1, _id: 1 } }
]);
```

Read records of `category,amount`, sum per category, then print them sorted by total descending and category ascending as tiebreaker.

See the prompt file for I/O specifics.
