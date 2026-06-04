# Embedded vs Referenced Relationship Resolver

MongoDB supports both embedded documents and references between collections. Simulate the "reference" model by resolving order references for each user.

## Input Format

```
U
userId1:name1
userId2:name2
...  (U user lines)
O
orderId1:userId1:amount1
orderId2:userId2:amount2
...  (O order lines)
```

- Line 1: integer U (number of users).
- Next U lines: `userId:name` pairs.
- Then: integer O (number of orders).
- Next O lines: `orderId:userId:amount` triples, where amount is a non-negative integer.

## Output Format

For each user, **in the order they appeared in the input**, print:

```
<name>: <count> orders, total: <sum>
```

Where `count` is the number of orders referencing that user and `sum` is the sum of their amounts. Users with no orders get `0 orders, total: 0`.

## Example

**Input:**
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

**Output:**
```
Alice: 2 orders, total: 250
Bob: 2 orders, total: 250
Carol: 0 orders, total: 0
```

## Notes

- User IDs and order IDs are unique strings within their respective groups.
- An order's `userId` always references a valid user in the input.
- Output order follows user input order, not alphabetical.
- There are no spaces around the `:` delimiters.
