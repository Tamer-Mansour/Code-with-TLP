# Exercise: Simulate MongoDB Query Filtering

In this exercise you will simulate the core logic of a MongoDB `find` query with filter operators. Your program reads a list of documents and a filter, then outputs the matching documents.

This mirrors what the MongoDB server does internally when evaluating `$gt`, `$lt`, `$eq`, and `$in` operators against a collection.

## Input Format

```
N
field op value
doc1_field1:val1 doc1_field2:val2 ...
doc2_field1:val1 ...
...
```

- Line 1: integer `N` — number of documents.
- Line 2: the filter — a single condition `field op value` where `op` is one of `eq`, `gt`, `lt`, `gte`, `lte`.
- Next `N` lines: documents, each as space-separated `key:value` pairs (all values are integers).

## Output Format

One line per matching document (in input order). Each line is the document's fields joined by spaces in the same order as they appeared in input. If no documents match, print `none`.

## Example

Input:
```
3
age gt 25
name:Alice age:30
name:Bob age:20
name:Carol age:35
```

Output:
```
name:Alice age:30
name:Carol age:35
```
