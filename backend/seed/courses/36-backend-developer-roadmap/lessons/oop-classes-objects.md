# OOP: Classes and Objects

Object-Oriented Programming (OOP) is the foundation of Java. Every piece of code you write lives inside a class, and nearly every value you work with at runtime is an object. Understanding what classes and objects are — and how they relate to each other — is the single most important mental model to build before moving on to inheritance, interfaces, or Spring.

## What is a Class?

A **class** is a blueprint. It defines:

- **Fields** — the data each object will carry (state).
- **Methods** — the actions each object can perform (behavior).
- **Constructors** — special blocks that initialise a new object.

The class itself is not an object; it is the description of what objects of that type look like.

## What is an Object?

An **object** (also called an *instance*) is a concrete value created from a class blueprint. Each object has its own independent copy of the fields defined in the class. You create an object with the `new` keyword.

```java
// Blueprint
public class Product {
    // Fields (state)
    private String name;
    private double price;
    private int stock;

    // Constructor
    public Product(String name, double price, int stock) {
        if (price < 0) throw new IllegalArgumentException("Price cannot be negative");
        if (stock < 0) throw new IllegalArgumentException("Stock cannot be negative");
        this.name  = name;
        this.price = price;
        this.stock = stock;
    }

    // Accessor (getter)
    public String getName()  { return name; }
    public double getPrice() { return price; }
    public int    getStock() { return stock; }

    // Mutator (method with business logic)
    public void restock(int units) {
        if (units <= 0) throw new IllegalArgumentException("Units must be positive");
        this.stock += units;
    }

    public boolean purchase(int quantity) {
        if (quantity <= 0 || quantity > stock) return false;
        this.stock -= quantity;
        return true;
    }

    @Override
    public String toString() {
        return String.format("Product{name='%s', price=%.2f, stock=%d}", name, price, stock);
    }
}
```

Creating and using objects:

```java
public class Main {
    public static void main(String[] args) {
        Product laptop = new Product("Laptop", 999.99, 10);
        Product mouse  = new Product("Mouse",   29.99, 50);

        System.out.println(laptop);          // Product{name='Laptop', price=999.99, stock=10}
        System.out.println(mouse.getStock()); // 50

        boolean sold = laptop.purchase(3);
        System.out.println(sold);            // true
        System.out.println(laptop.getStock()); // 7

        mouse.restock(20);
        System.out.println(mouse.getStock()); // 70

        // laptop and mouse are independent objects — different memory, different state
        System.out.println(laptop == mouse); // false
    }
}
```

`laptop` and `mouse` share the same `Product` blueprint, but their field values are completely independent.

## Class Anatomy at a Glance

| Member | Keyword/Placement | Purpose |
|---|---|---|
| Field | declared inside the class, outside methods | Stores object state |
| Constructor | same name as class, no return type | Initialises fields when `new` is called |
| Getter | `getXxx()` convention | Reads a private field safely |
| Setter | `setXxx()` convention | Writes a private field with optional validation |
| Instance method | any non-`static` method | Operates on the object's own fields |
| `static` member | `static` keyword | Belongs to the class, not any one object |
| `@Override toString()` | `java.lang.Object` contract | Readable text representation |

## The `this` Keyword

Inside any instance method or constructor, `this` refers to the object that received the call. It is most often used to disambiguate when a constructor parameter shadows a field:

```java
public Product(String name, double price, int stock) {
    this.name  = name;   // this.name = field, name = parameter
    this.price = price;
    this.stock = stock;
}
```

## Encapsulation: Keep Fields Private

Declare fields `private` and expose only what callers need through public methods. This lets you enforce rules (like "price cannot be negative") in one place and change the internal representation later without breaking callers.

```java
// Bad — public field lets anyone corrupt state
public double price;   // caller can write: laptop.price = -5;

// Good — private field, controlled access
private double price;
public double getPrice() { return price; }
public void setPrice(double price) {
    if (price < 0) throw new IllegalArgumentException("Price cannot be negative");
    this.price = price;
}
```

## Static vs Instance Members

A `static` field or method belongs to the **class itself**, not to any particular object. Use it for shared configuration or utility logic.

```java
public class Product {
    private static int totalCreated = 0;   // shared across ALL instances

    public Product(String name, double price, int stock) {
        // ... field assignments ...
        totalCreated++;
    }

    public static int getTotalCreated() {
        return totalCreated;
    }
}

// Usage
Product a = new Product("Keyboard", 49.99, 100);
Product b = new Product("Monitor",  299.99, 25);
System.out.println(Product.getTotalCreated()); // 2  — called on the class, not an object
```

## Common Mistakes

- **Forgetting `new`** — writing `Product p = Product(...)` is a compile error; you need `new`.
- **`NullPointerException` on uninitialised references** — declaring `Product p;` without assigning means `p` is `null`; calling any method on it throws NPE.
- **Public fields** — exposes internals and bypasses validation; always prefer `private` fields.
- **Skipping constructor validation** — constructors are the best place to reject illegal state before an invalid object ever exists.
- **Confusing `static` and instance** — calling `this.totalCreated` compiles but is misleading; access static members via the class name.

## Summary

A **class** is the blueprint describing fields and methods; an **object** is a live instance with its own state created via `new`. Keeping fields `private` and funnelling all access through methods (encapsulation) keeps invariants intact and makes code easy to change safely.
