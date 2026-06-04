# Quiz - Types, Traits, and Generics

Test your understanding of Rust's trait system, generics, and dispatch mechanisms.

## Question 1

What is the difference between static dispatch (generics with trait bounds) and dynamic dispatch (`dyn Trait`)?

- [ ] Static dispatch uses a vtable; dynamic dispatch is monomorphized
- [x] Static dispatch is monomorphized at compile time with no runtime overhead; dynamic dispatch uses a vtable with a pointer indirection per call
- [ ] They are functionally identical and the compiler chooses the faster one automatically
- [ ] Dynamic dispatch is always faster because the binary is smaller

## Question 2

Which of the following correctly adds a trait bound requiring `T` to implement both `Clone` and `Debug`?

- [ ] `fn foo<T: Clone || Debug>(x: T)`
- [ ] `fn foo<T: Clone, Debug>(x: T)`
- [x] `fn foo<T: Clone + Debug>(x: T)`
- [ ] `fn foo<T implements Clone + Debug>(x: T)`

## Question 3

What is a **default method** in a trait?

- [ ] A method that is automatically derived by the compiler
- [x] A method with a body defined in the trait itself; implementing types may override it or use the default
- [ ] A method that can only be called on the `Default` type
- [ ] A method that panics unless overridden

## Question 4

When is a trait **object-safe** (usable as `dyn Trait`)?

- [ ] When all its methods are `pub`
- [ ] When it has no associated types
- [x] When none of its methods return `Self` or use generic type parameters, and it has no `Sized` requirement
- [ ] When it derives `Clone` and `Debug`

## Question 5

What does **monomorphization** mean in Rust?

- [ ] The compiler checks that only one implementation of a trait exists
- [x] The compiler generates a separate copy of a generic function for each concrete type it is called with
- [ ] The runtime selects the correct implementation at first call
- [ ] Trait methods are merged into a single function pointer table

## Question 6

Which trait must `T` implement for it to be used as a key in a `HashMap<T, V>`?

- [ ] `Clone + Debug`
- [ ] `PartialOrd + Ord`
- [x] `Eq + Hash`
- [ ] `Display + FromStr`

## Question 7

What is the purpose of the `where` clause in a generic function?

- [ ] It specifies which crate a type comes from
- [x] It expresses trait bounds in a separate, more readable location — especially useful when bounds are complex
- [ ] It restricts a function to only work at a specific scope
- [ ] It replaces the lifetime annotation

## Question 8

A `dyn Trait` value is a **fat pointer**. What are the two pointers it contains?

- [ ] A pointer to the data and a pointer to the source file
- [x] A pointer to the data and a pointer to the vtable (virtual dispatch table)
- [ ] A pointer to the heap allocation and a pointer to the reference count
- [ ] A pointer to the type name and a pointer to the data
