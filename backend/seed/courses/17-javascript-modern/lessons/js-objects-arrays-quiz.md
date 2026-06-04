# Quiz: Objects and Arrays

**Q1. What does object destructuring with a default look like?**
```javascript
const { name = 'Anonymous', age } = user;
```
- [ ] `name` will always be `'Anonymous'` regardless of the object
- [x] `name` uses `'Anonymous'` only if `user.name` is `undefined`
- [ ] This is a syntax error
- [ ] `name` uses `'Anonymous'` if `user.name` is falsy

**Q2. What is the output of this code?**
```javascript
const a = [1, 2, 3];
const b = [...a];
b.push(4);
console.log(a.length);
```
- [x] `3`
- [ ] `4`
- [ ] `undefined`
- [ ] Throws an error

**Q3. Which array method returns a new array without mutating the original?**
- [ ] `push`
- [ ] `splice`
- [x] `slice`
- [ ] `sort` (always)

**Q4. What does `Object.entries({ a: 1, b: 2 })` return?**
- [ ] `['a', 'b']`
- [ ] `[1, 2]`
- [x] `[['a', 1], ['b', 2]]`
- [ ] `{ a: 1, b: 2 }`

**Q5. What is the difference between shallow copy and deep copy?**
- [ ] They are the same for all JavaScript objects
- [ ] Deep copy only works with arrays, not plain objects
- [x] Shallow copy duplicates the top-level references; nested objects are still shared. Deep copy duplicates all nested structures.
- [ ] Shallow copy uses `Object.assign`, deep copy uses the spread operator

**Q6. What does `[1, 2, 3].find(x => x > 1)` return?**
- [ ] `[2, 3]`
- [x] `2`
- [ ] `1`
- [ ] `true`

**Q7. Which of the following correctly merges two objects, with `b` taking precedence?**
- [ ] `Object.keys(a, b)`
- [x] `{ ...a, ...b }`
- [ ] `a + b`
- [ ] `Object.merge(a, b)`
