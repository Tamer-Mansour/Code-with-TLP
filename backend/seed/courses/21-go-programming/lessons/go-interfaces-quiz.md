# Quiz: Functions, Structs, and Interfaces

**Q1. How does a type satisfy an interface in Go?**
- [ ] By using the `implements` keyword
- [x] By defining all the methods the interface requires, with no explicit declaration
- [ ] By embedding the interface in the struct
- [ ] By registering the type with a central interface registry

**Q2. What is the method set of a pointer type `*T`?**
- [ ] Only methods with pointer receivers
- [ ] Only methods with value receivers
- [x] Methods with both value receivers and pointer receivers
- [ ] No methods — pointers cannot have methods in Go

**Q3. An interface value in Go is nil only when:**
- [ ] The concrete value stored in it is nil
- [ ] The interface variable was declared but never used
- [x] Both the dynamic type and the dynamic value are unset (truly untyped nil)
- [ ] The concrete type is a pointer type

**Q4. Which interface is satisfied by any type that has a `String() string` method?**
- [ ] io.Reader
- [ ] error
- [x] fmt.Stringer
- [ ] io.Writer

**Q5. What does the following type switch do?**
```go
switch v := x.(type) {
case string:
    ...
}
```
- [ ] Converts `x` to a string
- [x] Checks the dynamic type of `x` at runtime and binds it to `v` if it is a string
- [ ] Panics if `x` is not a string
- [ ] Compares `x` to the string type at compile time

**Q6. The Go convention for struct embedding is best described as:**
- [ ] Inheritance — the embedding type IS-A the embedded type
- [x] Composition — the embedding type HAS-A the embedded type, with promoted fields and methods
- [ ] Decoration — wraps the embedded type to add behavior
- [ ] Mixins — copies methods at compile time

**Q7. A nil pointer to a concrete type stored in an interface variable:**
- [ ] Makes the interface nil
- [ ] Causes a compile error
- [x] Produces a non-nil interface because the type descriptor is set
- [ ] Panics at runtime immediately
