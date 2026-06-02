# Quiz: Advanced TypeScript Types

Test your knowledge of generics, conditional types, and utility types.

**Q1. What is the type of `first` after: `const first = [1, 2, 3][0]` with `noUncheckedIndexedAccess` enabled?**
- [ ] `number`
- [x] `number | undefined`
- [ ] `1`
- [ ] `any`

**Q2. Which utility type removes `null` and `undefined` from a type?**
- [ ] `Partial<T>`
- [ ] `Required<T>`
- [x] `NonNullable<T>`
- [ ] `Exclude<T, U>`

**Q3. `Readonly<T>` makes all properties:**
- [x] Read-only at the compile-time type level only
- [ ] Immutable at runtime using `Object.freeze`
- [ ] Optional
- [ ] Non-nullable

**Q4. Given `type Keys = keyof { a: number; b: string }`, what is `Keys`?**
- [ ] `string`
- [ ] `number`
- [x] `"a" | "b"`
- [ ] `{ a: number; b: string }`

**Q5. `Pick<User, "name" | "email">` produces a type that:**
- [x] Has only the `name` and `email` properties of `User`
- [ ] Removes `name` and `email` from `User`
- [ ] Makes `name` and `email` optional
- [ ] Makes all properties of `User` optional except `name` and `email`

**Q6. What does `infer R` do in `T extends Promise<infer R> ? R : never`?**
- [ ] Casts `T` to `R`
- [x] Captures the resolved type of the `Promise` into `R`
- [ ] Checks if `R` extends `T`
- [ ] Makes `R` a union with `never`

**Q7. A mapped type `{ [K in keyof T]: T[K] | null }` produces:**
- [ ] A type identical to `T`
- [x] A type where every property of `T` can also be `null`
- [ ] A type where every property is optional
- [ ] A `Partial<T>` equivalent

**Q8. `Omit<Config, "password">` is equivalent to:**
- [x] `Pick<Config, Exclude<keyof Config, "password">>`
- [ ] `Partial<Config>`
- [ ] `Required<Config>`
- [ ] `Record<keyof Config, unknown>`

**Q9. Generics are erased at compile time. Which of the following is NOT possible at runtime?**
- [ ] Calling a generic function with a specific type argument
- [ ] Returning a generic value
- [x] Using `T` to check the runtime type of a value with `instanceof T`
- [ ] Passing a generic array to a function

**Q10. `Extract<"a" | "b" | "c", "a" | "c">` evaluates to:**
- [ ] `"b"`
- [x] `"a" | "c"`
- [ ] `never`
- [ ] `"a" | "b" | "c"`
