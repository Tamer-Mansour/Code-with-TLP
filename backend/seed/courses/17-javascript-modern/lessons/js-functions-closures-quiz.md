# Quiz: Functions and Closures

**Q1. What is the key difference between an arrow function and a regular function regarding `this`?**
- [ ] Arrow functions cannot accept parameters
- [ ] Arrow functions run faster at runtime
- [x] Arrow functions inherit `this` from their enclosing lexical scope; they have no own `this`
- [ ] Arrow functions automatically bind `this` to the global object

**Q2. What does the following code print?**
```javascript
function makeAdder(x) {
  return (y) => x + y;
}
const add5 = makeAdder(5);
console.log(add5(3));
```
- [ ] `undefined`
- [ ] `NaN`
- [x] `8`
- [ ] Throws a ReferenceError

**Q3. Which statement about `let` and the Temporal Dead Zone (TDZ) is correct?**
- [ ] `let` is not hoisted at all
- [x] `let` is hoisted but not initialized; accessing it before its declaration throws ReferenceError
- [ ] `let` is hoisted and initialized to `undefined`, same as `var`
- [ ] `let` is only hoisted inside `for` loops

**Q4. Can an arrow function be used as a constructor (called with `new`)?**
- [ ] Yes, it works the same as a regular function
- [ ] Yes, but only if it returns an object literal
- [x] No, calling an arrow function with `new` throws a TypeError
- [ ] Yes, but `this` will be `undefined` inside it

**Q5. What does the following IIFE pattern accomplish?**
```javascript
const result = (() => {
  const secret = 42;
  return secret * 2;
})();
```
- [ ] It throws a SyntaxError because arrow functions cannot be immediately invoked
- [ ] It creates a global variable `secret`
- [x] It creates a private scope for `secret` and immediately returns `84`
- [ ] It runs asynchronously

**Q6. What will `fn.bind({a: 1}).call({a: 2})` use as `this`?**
- [ ] `{a: 2}` because `call` always wins
- [x] `{a: 1}` because `bind` locks `this` permanently
- [ ] `undefined` because they conflict
- [ ] The global object

**Q7. What are the three things arrow functions lack compared to regular functions?**
- [ ] `return`, `arguments`, `prototype`
- [x] Own `this` binding, `arguments` object, ability to be used as constructor
- [ ] Default parameters, rest parameters, destructuring
- [ ] Recursion, closures, hoisting
