# Quiz: TypeScript Patterns

Test your understanding of function types, classes, conditional types, and modules.

**Q1. What does `ReturnType<typeof fn>` produce?**
- [ ] The type of the function itself
- [ ] The type of the first parameter
- [x] The return type of the function `fn`
- [ ] A union of all parameter types

**Q2. Which access modifier provides true runtime privacy in TypeScript classes?**
- [ ] `private`
- [ ] `protected`
- [x] `#` (JavaScript private fields)
- [ ] `readonly`

**Q3. What does `T extends U ? X : Y` do when `T` is a union type?**
- [ ] Evaluates only once with the full union as `T`
- [x] Distributes over each member of the union separately
- [ ] Throws a compile error
- [ ] Always resolves to `X`

**Q4. Which `tsconfig` `moduleResolution` setting is recommended for modern Vite/esbuild projects?**
- [ ] `"node"`
- [ ] `"classic"`
- [x] `"bundler"`
- [ ] `"node16"`

**Q5. An `async` function annotated as `Promise<number>` that returns a `string` will:**
- [ ] Return the string at runtime silently
- [ ] Produce a runtime error
- [x] Produce a TypeScript compile-time error
- [ ] Return `undefined`

**Q6. The `satisfies` operator (TS 4.9+) is used to:**
- [ ] Cast a value to a wider type
- [ ] Suppress type errors globally
- [x] Validate that a value matches a type without widening its inferred type
- [ ] Replace `instanceof` checks

**Q7. What is the purpose of a `asserts x is T` return type annotation?**
- [ ] It makes the function return a boolean
- [x] It tells TypeScript that if the function returns normally, `x` is narrowed to `T` from that point on
- [ ] It asserts the type at runtime using `typeof`
- [ ] It creates a new type alias `T`

**Q8. Barrel files (`index.ts`) are primarily used for:**
- [ ] Circular imports
- [ ] Lazy loading
- [x] Aggregating and re-exporting a module's public API from one path
- [ ] Declaring ambient globals

**Q9. Which decorator type can fully replace the implementation of a class method?**
- [ ] Class decorator
- [ ] Property decorator
- [ ] Parameter decorator
- [x] Method decorator

**Q10. The `infer` keyword in conditional types is used to:**
- [ ] Import a type from another module
- [ ] Extend a type constraint
- [x] Capture and name a type within the matched pattern of a conditional type
- [ ] Assert that a value is non-null
