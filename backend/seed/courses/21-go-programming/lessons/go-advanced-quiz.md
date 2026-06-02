# Quiz: Generics and Advanced Patterns

**Q1. What keyword introduces a type parameter in a Go generic function?**
- [ ] `template`
- [x] `[T ...]` (square brackets after the function name)
- [ ] `generic`
- [ ] `type`

**Q2. Which built-in constraint allows using `==` and `!=` on a type parameter?**
- [ ] `any`
- [ ] `Number`
- [x] `comparable`
- [ ] `Equatable`

**Q3. A `Stack[T any]` is defined with `Push` and `Pop`. Which statement is correct?**
- [ ] You must specify T when calling Push: `s.Push[string]("hello")`
- [x] Go infers T from the argument: `s.Push("hello")` is valid
- [ ] Methods on generic types cannot have type parameters
- [ ] `Stack` can only hold pointer types

**Q4. Which Go version introduced generics?**
- [ ] 1.14
- [ ] 1.16
- [x] 1.18
- [ ] 1.21

**Q5. When is it best NOT to use generics?**
- [ ] When writing a reusable data structure like a Set
- [x] When a plain interface or `any` is simpler and the logic is used with one type
- [ ] When implementing Map/Filter/Reduce over slices
- [ ] When writing Min/Max over numeric types

**Q6. What does the `slices` package (Go 1.21+) use internally to be type-safe?**
- [ ] Reflection (`reflect` package)
- [ ] Type assertions on `any`
- [x] Generics
- [ ] Code generation with `go generate`

**Q7. Which interface union correctly constrains a type to signed 32-bit and 64-bit integers only?**
- [ ] `int | uint`
- [x] `int32 | int64`
- [ ] `comparable | int`
- [ ] `Number | Float`

**Q8. Given `func Map[T, U any](s []T, fn func(T) U) []U`, what is the return type of `Map([]int{1,2,3}, strconv.Itoa)`?**
- [ ] `[]any`
- [x] `[]string`
- [ ] `[]int`
- [ ] Compile error — two type parameters require explicit specification
