# Inventory Filter with Streams

Read `N` on the first line. Then read `N` lines, each containing a product name (no spaces) and an integer price separated by a single space. Finally read an integer budget `B` on the last line.

Print the names **and prices** of all products with price **≤ B**, one per line, sorted by price ascending. If two products share the same price, sort alphabetically by name (case-sensitive, lowercase < uppercase by ASCII). If no products qualify, print `No items found`.

## Input format

```
N
name1 price1
name2 price2
...
B
```

## Output format

```
name price
...
```

or if nothing qualifies:

```
No items found
```

## Example

**Input**
```
5
apple 2
banana 1
cherry 5
date 3
elderberry 1
3
```

**Output**
```
banana 1
elderberry 1
apple 2
date 3
```

## Constraints

- `1 <= N <= 100`
- Product names contain only lowercase letters and digits, no spaces.
- `1 <= price <= 10^4`
- `1 <= B <= 10^4`
