# Quiz: Narrowing and Unions

Test your understanding of TypeScript's type narrowing, discriminated unions, and exhaustiveness checking.

**Q1. After `if (typeof x === "string")`, inside the true branch TypeScript narrows `x` to:**
- [x] `string`
- [ ] `string | undefined`
- [ ] `unknown`
- [ ] `any`

**Q2. A discriminated union requires each member to have:**
- [ ] A different number of properties
- [x] A shared field with a unique literal type per variant (the discriminant)
- [ ] At least one optional property
- [ ] The same set of methods

**Q3. The "exhaustiveness trick" uses `never` like this: `const _x: never = s`. This errors when:**
- [ ] `s` is `null`
- [ ] `s` is `undefined`
- [x] `s` is not `never` — i.e., you missed a case in a switch and a union variant is unhandled
- [ ] `s` is an object type

**Q4. A user-defined type guard function has return type:**
- [ ] `boolean`
- [x] `value is SomeType`
- [ ] `narrowed<SomeType>`
- [ ] `typeof SomeType`

**Q5. TypeScript's `in` operator can narrow a type. `"fly" in x` narrows `x` to:**
- [x] Types in the union that have a `fly` property
- [ ] The type `string`
- [ ] `never` if `fly` doesn't exist on any member
- [ ] `unknown`

**Q6. Control flow analysis means:**
- [ ] TypeScript rewrites your control flow for performance
- [x] TypeScript tracks which types are possible at each point in the code based on the branches taken
- [ ] TypeScript inserts runtime checks automatically
- [ ] TypeScript prevents unreachable code from compiling
