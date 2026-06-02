# Control Flow and Arrays

Java provides the familiar C-style control structures plus some modern additions.

## Conditionals

```java
int score = 85;

if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else {
    System.out.println("C or below");
}
```

Java 14+ adds **switch expressions** — a cleaner form that returns a value:

```java
String grade = switch (score / 10) {
    case 10, 9 -> "A";
    case 8     -> "B";
    case 7     -> "C";
    default    -> "F";
};
```

## Loops

```java
// Classic for
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// Enhanced for (for-each)
int[] nums = {1, 2, 3};
for (int n : nums) {
    System.out.println(n);
}

// while
int x = 0;
while (x < 3) {
    System.out.println(x++);
}

// do-while (body runs at least once)
int y = 0;
do {
    System.out.println("y=" + y);
    y++;
} while (y < 3);
```

## break and continue

```java
for (int i = 0; i < 10; i++) {
    if (i == 5) break;      // exit loop
    if (i % 2 == 0) continue; // skip even
    System.out.println(i);  // prints 1 3
}
```

Labeled breaks let you exit nested loops:

```java
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (i == 1 && j == 1) break outer;
        System.out.println(i + "," + j);
    }
}
```

## Arrays

Arrays are fixed-size, zero-indexed, and strongly typed.

```java
int[] arr = new int[5];         // default-initialized to 0
arr[0] = 10;

int[] primes = {2, 3, 5, 7};   // inline initializer
System.out.println(primes.length); // 4

String[] names = new String[3];  // null by default
```

### Common array operations

```java
import java.util.Arrays;

int[] data = {5, 3, 8, 1};
Arrays.sort(data);                       // {1, 3, 5, 8}
System.out.println(Arrays.toString(data)); // [1, 3, 5, 8]
int idx = Arrays.binarySearch(data, 5); // 2
int[] copy = Arrays.copyOf(data, 3);    // [1, 3, 5]
```

### 2D arrays

```java
int[][] matrix = new int[3][3];
matrix[0][0] = 1;

int[][] grid = {
    {1, 2, 3},
    {4, 5, 6}
};
System.out.println(grid[1][2]); // 6
```

## Varargs

```java
public static int sum(int... nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}

sum(1, 2, 3);      // 6
sum(1, 2, 3, 4);   // 10
```

## Quick Reference

| Construct         | Java syntax                              |
|-------------------|------------------------------------------|
| Classic for       | `for (int i = 0; i < n; i++)`           |
| Enhanced for      | `for (Type x : collection)`             |
| Switch expression | `switch (v) { case A -> ...; }`         |
| Array declare     | `int[] arr = new int[n];`               |
| Array literal     | `int[] arr = {1, 2, 3};`               |
| Array length      | `arr.length`                            |
| Sort              | `Arrays.sort(arr)`                      |
