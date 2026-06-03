# Quiz: Java Foundations

Test your understanding of Java syntax, object-oriented principles, the Collections Framework, and exception handling covered in this module. Each question has exactly one correct answer.

---

**Q1. What is the output of the following program?**

```java
public class Main {
    public static void main(String[] args) {
        int x = 5;
        System.out.println(x++);
        System.out.println(x);
    }
}
```

- [ ] `6` then `6`
- [x] `5` then `6`
- [ ] `5` then `5`
- [ ] `6` then `5`

---

**Q2. Which statement correctly describes the difference between `==` and `.equals()` when comparing two `String` objects in Java?**
- [ ] `==` compares content; `.equals()` compares memory addresses
- [ ] Both `==` and `.equals()` always compare content for any object
- [x] `==` compares object references (memory addresses); `.equals()` compares the actual character content of the strings
- [ ] `.equals()` is only available on primitive wrapper types like `Integer`

---

**Q3. Given the following class, which keyword enforces that `balance` cannot be accessed directly from outside the class?**

```java
public class BankAccount {
    private double balance;

    public double getBalance() {
        return balance;
    }

    public void deposit(double amount) {
        if (amount > 0) balance += amount;
    }
}
```

- [ ] `public`
- [ ] `protected`
- [x] `private`
- [ ] `static`

---

**Q4. A method in a subclass has the same name, return type, and parameter list as a method in its superclass. What Java concept does this represent?**
- [ ] Method overloading
- [ ] Method hiding
- [ ] Shadowing
- [x] Method overriding

---

**Q5. What does the following code print?**

```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>();
        names.add("Alice");
        names.add("Bob");
        names.add("Alice");
        System.out.println(names.size());
    }
}
```

- [ ] `1`
- [ ] `2`
- [x] `3`
- [ ] Compilation error — `List` does not allow duplicates

---

**Q6. You need to store a mapping from student IDs (`int`) to student names (`String`) and look up a name in O(1) average time. Which Java Collections class is the best fit?**
- [ ] `ArrayList<String>`
- [ ] `LinkedList<String>`
- [x] `HashMap<Integer, String>`
- [ ] `TreeSet<String>`

---

**Q7. Which of the following correctly handles a checked exception thrown by `Integer.parseInt()`?**

```java
// Option A
String input = "abc";
int value = Integer.parseInt(input);

// Option B
String input = "abc";
try {
    int value = Integer.parseInt(input);
} catch (NumberFormatException e) {
    System.out.println("Invalid number: " + e.getMessage());
}
```

- [ ] Option A — `NumberFormatException` is a checked exception and must be declared with `throws`
- [ ] Both options compile and run identically
- [x] Option B — `NumberFormatException` is an unchecked (`RuntimeException`) exception; wrapping it in `try-catch` prevents the program from crashing on invalid input
- [ ] Neither option compiles because `parseInt` returns a `String`

---

**Q8. An `interface` in Java 17 can contain which of the following?**

| Member type | Allowed in interface? |
|---|---|
| Abstract method (no body) | Yes |
| `default` method (with body) | Yes |
| `static` method (with body) | Yes |
| Instance field (non-`static`) | No |

- [ ] Only abstract methods — interfaces cannot have any method bodies
- [ ] Abstract methods and instance fields, but no `default` or `static` methods
- [ ] Only `default` and `static` methods; abstract methods require an abstract class
- [x] Abstract methods, `default` methods with a body, and `static` methods with a body — but not non-`static` instance fields

---

**Q9. What is the output of the following snippet?**

```java
public class Animal {
    public String sound() { return "..."; }
}

public class Dog extends Animal {
    @Override
    public String sound() { return "Woof"; }
}

public class Main {
    public static void main(String[] args) {
        Animal a = new Dog();
        System.out.println(a.sound());
    }
}
```

- [ ] `...`
- [x] `Woof`
- [ ] Compilation error — `Animal` reference cannot point to a `Dog` object
- [ ] `null`

---

**Q10. Which statement about `static` members in Java is correct?**
- [ ] A `static` method can access instance variables of its class directly
- [ ] `static` fields are garbage-collected when the object is deallocated
- [ ] Each object instance gets its own copy of a `static` field
- [x] A `static` field is shared across all instances of the class, and a `static` method can be called without creating an object
