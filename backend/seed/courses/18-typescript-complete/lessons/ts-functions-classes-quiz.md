# Quiz: Functions and Classes

Test your understanding of TypeScript function types, overloads, class modifiers, and structural typing.

**Q1. Which modifier makes a class property settable ONLY inside the constructor?**
- [ ] `private`
- [ ] `protected`
- [x] `readonly`
- [ ] `static`

**Q2. The `override` keyword in TypeScript (4.3+) causes a compile error when:**
- [ ] You call `super()` in the constructor
- [x] The overridden method does not exist in the parent class
- [ ] The method has a different return type
- [ ] The method is `private`

**Q3. What does TypeScript's "parameter properties" shorthand do?**
- [ ] Makes all constructor parameters optional
- [x] Declares and assigns class fields in one step using access modifier prefixes in the constructor
- [ ] Converts parameters to `readonly` automatically
- [ ] Infers types from default values only

**Q4. Two classes with identical field shapes but no declared relationship are:**
- [ ] Incompatible — TypeScript uses nominal typing
- [x] Mutually assignable — TypeScript uses structural (duck) typing
- [ ] Compatible only if they both implement the same interface
- [ ] Compatible only if they extend the same base class

**Q5. In an overloaded function, which signature is visible to callers?**
- [x] Only the declared overload signatures, not the implementation signature
- [ ] Only the implementation signature
- [ ] All signatures equally
- [ ] The last declared signature only

**Q6. `abstract` classes differ from interfaces because:**
- [ ] Abstract classes cannot be extended
- [ ] Abstract classes support declaration merging
- [x] Abstract classes can contain implemented (non-abstract) methods; interfaces cannot
- [ ] Abstract classes generate runtime JavaScript; interfaces do not

**Q7. TypeScript's `private` keyword vs JavaScript's `#` private field: which provides true runtime encapsulation?**
- [ ] TypeScript's `private` keyword
- [x] JavaScript's `#` private field syntax
- [ ] Both provide the same level of encapsulation
- [ ] Neither — TypeScript always compiles to public fields
