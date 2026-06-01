# Array Methods - map, filter, reduce

Arrays are the workhorse data structure. Modern JS has a rich set of methods that replace most `for` loops.

## map — transform each item

```javascript
[1, 2, 3].map(x => x * x);        // [1, 4, 9]

users.map(u => ({
  id: u.id,
  display: `${u.firstName} ${u.lastName}`,
}));
```

Returns a new array of the same length. **Never mutate** the source.

## filter — keep matching items

```javascript
[1, 2, 3, 4].filter(x => x % 2 === 0);    // [2, 4]
users.filter(u => u.isActive);
```

## reduce — collapse to a single value

```javascript
[1, 2, 3].reduce((acc, x) => acc + x, 0);     // 6
[1, 2, 3].reduce((acc, x) => acc * x, 1);     // 6
```

Group by key:

```javascript
users.reduce((acc, u) => {
  (acc[u.country] ||= []).push(u);
  return acc;
}, {});
```

Use for: sum, product, building an object/Map, custom aggregations. Don't reach for `reduce` when a `for` loop is clearer — readability beats cleverness.

## forEach — side effects only

```javascript
items.forEach(x => console.log(x));
```

Returns `undefined`. Use when you need side effects and don't want a return value. For pure transformation, prefer `map`/`filter`/`reduce`.

## find / findIndex / findLast

```javascript
users.find(u => u.id === 42);              // first match, or undefined
users.findIndex(u => u.id === 42);         // index, or -1
users.findLast(u => u.isActive);
```

## some / every

```javascript
users.some(u => u.isAdmin);           // is any user admin?
users.every(u => u.isActive);         // are all active?
```

Short-circuit — they stop as soon as they know the answer.

## includes / indexOf

```javascript
[1, 2, 3].includes(2);                // true
["a", "b"].indexOf("c");              // -1
```

`includes` uses strict equality, with the bonus that `[NaN].includes(NaN) === true` (where `indexOf` says -1).

## sort

Mutates! Default sort is **lexicographic**, even for numbers:

```javascript
[10, 2, 1].sort();                    // [1, 10, 2]   ← bug
[10, 2, 1].sort((a, b) => a - b);     // [1, 2, 10]
```

Always supply a comparator. Return negative for "a before b", positive for "b before a", 0 for equal.

For an immutable sort:

```javascript
const sorted = [...arr].sort((a, b) => a - b);
```

Or modern `toSorted()` (2023):

```javascript
arr.toSorted((a, b) => a - b);
```

## flat / flatMap

```javascript
[[1, 2], [3, 4]].flat();              // [1, 2, 3, 4]
[[[1]], [[2]]].flat(2);               // [1, 2]
[1, 2].flatMap(x => [x, x * 10]);     // [1, 10, 2, 20]
```

`flatMap` is `map` then `flat(1)` — common when each item produces zero, one, or many outputs.

## Iteration chain

```javascript
const total = orders
  .filter(o => o.status === "paid")
  .map(o => o.amount)
  .reduce((a, b) => a + b, 0);
```

Reads top-down like a pipeline. Easier to follow than the equivalent loop.

## Performance note

Each call creates a new array. For tiny arrays it's irrelevant; for million-element pipelines, a single loop is faster:

```javascript
let total = 0;
for (const o of orders) {
  if (o.status === "paid") total += o.amount;
}
```

Pick clarity first; optimize only when profiling demands it.
