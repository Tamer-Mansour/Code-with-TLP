# Sum Squares of Evens

A classic JavaScript array pipeline:

```javascript
const total = nums
  .filter(n => n % 2 === 0)
  .map(n => n * n)
  .reduce((acc, n) => acc + n, 0);
```

Read whitespace-separated integers and print the sum of the squares of the even ones.

See the prompt for I/O specifics.
