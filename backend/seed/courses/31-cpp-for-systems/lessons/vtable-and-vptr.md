# How vtable and vptr Implement Virtual Dispatch

The vtable (virtual function table) is the data structure compilers use to implement runtime polymorphism. Understanding it demystifies virtual calls, helps you reason about memory layout, and is a near-universal interview topic for systems roles.

## What Is a vtable?

Every class that has at least one virtual function gets a **vtable** — a static, read-only array of function pointers, one per virtual function in the class's interface. There is one vtable per class (not per object). It lives in the read-only data segment.

Every object of that class carries a hidden **vptr** (virtual pointer) — a pointer to its class's vtable. The vptr is typically the **first** field of the object, so it adds one pointer-size (8 bytes on a 64-bit system) to every object.

## Memory Layout Illustration

```
class Shape {
    virtual double area() const;
    virtual void   draw() const;
    int color;
};

class Circle : Shape {
    void draw() const override;
    double area() const override;
    double radius;
};
```

```
Shape object layout:
+----------+
| vptr     |  --> Shape vtable: [ &Shape::area, &Shape::draw ]
| color    |
+----------+

Circle object layout:
+----------+
| vptr     |  --> Circle vtable: [ &Circle::area, &Circle::draw ]
| color    |  (inherited)
| radius   |
+----------+
```

## What Happens at a Virtual Call

```cpp
Shape* s = new Circle(5.0);
s->area();
```

At the machine level this becomes (pseudo-assembly):

```asm
mov  rax, [s]            ; 1. load vptr from object
mov  rax, [rax + 0]      ; 2. index into vtable (slot 0 = area)
call rax                 ; 3. indirect call
```

Three steps:
1. Dereference the object to get the vptr.
2. Index into the vtable at the appropriate slot offset.
3. Indirect call through that function pointer.

Compare to a direct (non-virtual) call which is a single `call <fixed address>` instruction.

## Constructing the vtable Step by Step

1. **Compiler assigns a slot index** to each virtual function in the base class.
2. **Derived class inherits** those slot indices.
3. **Overrides replace** the function pointer in the corresponding slot; non-overridden slots keep the base pointer.
4. **Constructor writes the vptr**: when an object is constructed, the generated constructor code stores the correct vtable address into the vptr field — first the base vtable is installed (while the base sub-constructor runs), then the derived vtable is installed (once derived construction begins).

```cpp
struct A {
    virtual void f(); // slot 0
    virtual void g(); // slot 1
};

struct B : A {
    void f() override; // slot 0 → B::f  (replaced)
    // g not overridden → slot 1 stays A::g
    virtual void h();  // slot 2 → B::h  (new)
};

// B vtable: [ &B::f, &A::g, &B::h ]
```

## sizeof Impact

```cpp
struct NoVirtual { int x; };           // sizeof == 4
struct WithVirtual { virtual void f(); int x; }; // sizeof == 16 (vptr=8 + int=4 + padding=4)
```

Always account for this in cache-line and object-pool calculations.

## Multiple Inheritance and vtables

With multiple inheritance, an object may have **multiple vptrs** — one for each base class that has virtual functions. Casting between base pointers adjusts the pointer value accordingly (thunk mechanism), which is why casting a base pointer from one path of multiple inheritance to another can change the numerical address.

## RTTI and the vtable

The vtable also stores a pointer to `std::type_info` used by `typeid` and `dynamic_cast`. This means disabling RTTI (`-fno-rtti`) shrinks vtables slightly and speeds up link time, at the cost of losing `dynamic_cast` and `typeid`.

## Common Interview Gotcha

"Does adding a virtual function to a class change its size?"  
Yes — by one pointer if it is the first virtual function. Adding more virtual functions does not change the object size (only the vtable grows, which is shared).

**Interview answer:** Each polymorphic class has a static vtable (array of function pointers); each object has a vptr (first field) pointing to its class's vtable; a virtual call loads the vptr, indexes the vtable, and performs an indirect call — costing two extra memory reads compared to a direct call.
