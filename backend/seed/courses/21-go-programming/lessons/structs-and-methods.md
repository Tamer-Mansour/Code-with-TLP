# Structs and Methods

## Structs

```go
type User struct {
    ID    int64
    Name  string
    Email string
}

u := User{ID: 1, Name: "Alice", Email: "alice@x.com"}
u2 := User{1, "Bob", "bob@x.com"}     // positional, fragile
u3 := User{ID: 1}                      // zero values for missing fields
```

Access fields with `.`:

```go
u.Email = "alice@y.com"
```

## Methods

Methods are functions with a **receiver**:

```go
func (u User) Greet() string {
    return "Hi, " + u.Name
}
```

Value receiver — `u` is a copy.

```go
func (u *User) Rename(name string) {
    u.Name = name
}
```

Pointer receiver — `u` references the original. Use when you need to mutate, or when the struct is large.

### Convention

Use a pointer receiver if **any** method needs one, even if the others don't. Mixing value and pointer receivers on the same type is a source of bugs.

## Embedding

Go has no inheritance, but you can **embed** one struct into another:

```go
type Animal struct {
    Name string
}

func (a Animal) Speak() string { return "..." }

type Dog struct {
    Animal           // embedded - no field name
    Breed string
}

d := Dog{Animal: Animal{Name: "Rex"}, Breed: "Lab"}
d.Name       // promoted field
d.Speak()    // promoted method
```

The embedded type's fields and methods are "promoted" to the outer type. Composition with the ergonomics of inheritance, without the rigid hierarchy.

## Tags

```go
type User struct {
    ID    int64  `json:"id"            db:"id"`
    Name  string `json:"name"          db:"name"`
    Email string `json:"email,omitempty" db:"email"`
}
```

Tags are string metadata read by reflection. The `encoding/json` package uses them to control JSON field names; ORMs and validators do similar.

## Constructors are just functions

There's no `new()` keyword for custom types; convention is `New<Type>`:

```go
func NewUser(name, email string) *User {
    return &User{
        ID:    nextID(),
        Name:  name,
        Email: email,
    }
}
```

`&User{...}` allocates a `User` and returns a pointer to it. Go's escape analysis decides whether it lands on the stack or the heap.

## Visibility

**Exported** identifiers start with a capital letter; everything else is package-private.

```go
type user struct {        // unexported
    id    int64
    name  string
    Email string          // exported field (weird but legal)
}

func New() *user { ... }  // returns an unexported type — discouraged
```

Most public APIs use exported types and unexported fields with getters/setters when needed.

## String formatting

Implement `String() string` to control how your type prints:

```go
func (u User) String() string {
    return fmt.Sprintf("User<%d %s>", u.ID, u.Name)
}
```

`fmt.Println(u)` will now use it. The `%v` verb does too.

## Equality

Structs are comparable if **all fields** are comparable. Slices and maps aren't, so a struct containing them isn't either — define your own `Equals` method or use `reflect.DeepEqual`.
