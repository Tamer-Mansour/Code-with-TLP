# Exercise: FizzBuzz with Configurable Range

FizzBuzz is the classic programming interview warm-up. This version adds a twist: after printing the sequence, you must also print a count of the numbers that were printed as plain integers (i.e. not replaced by Fizz, Buzz, or FizzBuzz).

## Core concepts practised

- `for` loop with a counter variable
- `if / else if / else` ladder
- The modulus operator `%`
- Accumulating a count with a loop variable
- Formatted string output

## Java pattern

```java
int count = 0;
for (int i = 1; i <= n; i++) {
    if (i % 15 == 0) {
        System.out.println("FizzBuzz");
    } else if (i % 3 == 0) {
        System.out.println("Fizz");
    } else if (i % 5 == 0) {
        System.out.println("Buzz");
    } else {
        System.out.println(i);
        count++;
    }
}
System.out.println("Plain numbers: " + count);
```

Note: check divisibility by 15 *before* 3 or 5, because every multiple of 15 is also a multiple of both 3 and 5. If you check 3 first, multiples of 15 will be printed as "Fizz" instead of "FizzBuzz".

## Problem statement

Read two integers `N` and `M` from stdin (one per line). The second value `M` is present in the input but not used — it is there to match the spec format. Print every integer from 1 to `N` inclusive, replacing multiples of 3 with `Fizz`, multiples of 5 with `Buzz`, and multiples of both with `FizzBuzz`. After the sequence, print a final line: `Plain numbers: <count>` where `<count>` is the number of integers printed as plain numbers.

### Example

Input:
```
15
0
```

Output:
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
Plain numbers: 8
```

## Further reading

- *Think Java* (2nd ed.), Chapter 5 (Conditionals and Logic): https://greenteapress.com/wp/think-java-2e/
- MIT OCW 6.092, Lecture 2 — Types and Conditionals: https://ocw.mit.edu/courses/6-092-introduction-to-programming-in-java-january-iap-2010/
