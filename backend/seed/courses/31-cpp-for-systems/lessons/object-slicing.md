# Object Slicing: What It Is and How to Avoid It

Object slicing is one of the most insidious bugs in C++ inheritance. It is silent, produces no compiler warning by default, and produces incorrect behavior that is hard to diagnose. It occurs when a derived-class object is **copied into a base-class object by value**, stripping away all derived-class members and the vtable.

## What Happens During Slicing

```cpp
struct Animal {
    std::string name;
    virtual std::string sound() const { return "..."; }
};

struct Dog : Animal {
    std::string breed;
    std::string sound() const override { return "Woof"; }
};

Dog d;
d.name  = "Rex";
d.breed = "Husky";

Animal a = d;          // SLICING: copies only the Animal sub-object
                       // breed is lost; vptr points to Animal's vtable

std::cout << a.sound();   // "..." — Dog::sound is gone
```

After the assignment, `a` is a complete `Animal` object with:
- Only the `name` member (`breed` is discarded).
- The `Animal` vtable — so `a.sound()` calls `Animal::sound`.

## Slicing in Function Parameters

The most common trigger is passing a derived object to a function that takes a base type **by value**:

```cpp
void makeSound(Animal a) {         // takes by VALUE — slices!
    std::cout << a.sound() << '\n';
}

Dog d;
makeSound(d);    // copies only Animal part of d; prints "..."
```

Fix: pass by reference or pointer.

```cpp
void makeSound(const Animal& a) {  // by reference — no copy, no slice
    std::cout << a.sound() << '\n';
}
void makeSound(const Animal* a) {  // by pointer — same
    std::cout << a->sound() << '\n';
}
```

## Slicing in Containers

Storing derived objects in a container of base objects also slices:

```cpp
std::vector<Animal> zoo;
zoo.push_back(Dog{});    // slices to Animal — Dog::sound lost
zoo.push_back(Cat{});    // slices to Animal
```

Correct approach: store pointers (preferably smart pointers):

```cpp
std::vector<std::unique_ptr<Animal>> zoo;
zoo.push_back(std::make_unique<Dog>());
zoo.push_back(std::make_unique<Cat>());

for (auto& a : zoo) {
    std::cout << a->sound() << '\n';  // correct virtual dispatch
}
```

## How to Detect and Prevent Slicing

### Option 1: Delete copy operations in the base class

If the base class is meant to be used only polymorphically through pointers:

```cpp
struct Animal {
    Animal(const Animal&) = delete;
    Animal& operator=(const Animal&) = delete;
    virtual std::string sound() const = 0;
    virtual ~Animal() = default;
};
```

Any attempt to copy-by-value a derived object into `Animal` now results in a **compile error** — the best outcome.

### Option 2: Make the base class abstract

An abstract class (with at least one pure virtual) cannot be instantiated, which eliminates direct value-type variables of the base class. This partially prevents slicing since you cannot write `Animal a = d;` if `Animal` is abstract.

### Option 3: Compiler warnings

Clang provides `-Wsliced` and GCC `-Wextra` may warn in some cases, but these are not reliable. The best defense is architecture (delete the copy constructor, or use the abstract class pattern).

## Slicing with Assignment

Assignment can also slice silently:

```cpp
Dog d1, d2;
Animal& a = d1;
a = d2;           // calls Animal::operator= — only Animal members copied
                  // d1 still has a Dog vptr but may have inconsistent state
```

This is subtler because the vptr is not changed (it stays as `Dog`), but the derived members are not updated by the base assignment operator.

## Quick Reference

| Pattern | Slices? | Fix |
|---------|---------|-----|
| `Animal a = dog;` | Yes | Use `Animal&` or `Animal*` |
| `void f(Animal a)` | Yes | Use `void f(const Animal&)` |
| `vector<Animal>` | Yes | Use `vector<unique_ptr<Animal>>` |
| `Animal& a = dog;` | No | Already a reference |
| `Animal* a = &dog;` | No | Already a pointer |

**Interview answer:** Object slicing occurs when a derived-class object is copied into a base-class value, discarding derived members and the vtable; prevent it by always using references or pointers for polymorphic types, and by deleting the base class copy constructor to make accidental value-copy a compile error.
