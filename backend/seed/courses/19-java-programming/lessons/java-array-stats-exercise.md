# Exercise: Array Statistics

Working with arrays is a fundamental Java skill. This exercise practises the three most common array traversal patterns: finding a minimum, finding a maximum, and computing an average using an accumulator.

## The Java pattern

```java
int[] nums = {3, 7, 1, 9, 4, 6};
int min = nums[0];
int max = nums[0];
int sum = 0;

for (int n : nums) {
    if (n < min) min = n;
    if (n > max) max = n;
    sum += n;
}

double avg = (double) sum / nums.length;
System.out.printf("Min: %d%n", min);
System.out.printf("Max: %d%n", max);
System.out.printf("Average: %.2f%n", avg);
```

Key points:
- Initialise `min` and `max` to the first element, not to `0` — otherwise you'll get wrong answers for all-negative arrays.
- Cast to `double` before dividing to avoid integer division truncation.
- `%.2f` in `printf` rounds to exactly two decimal places.

## Problem statement

Read an integer `N` on the first line, then `N` space-separated integers on the second line. Print the minimum, maximum, and average of the array, each on its own line with a label, with the average rounded to **2 decimal places**.

### Example

Input:
```
6
3 7 1 9 4 6
```

Output:
```
Min: 1
Max: 9
Average: 5.00
```

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 7: Arrays: https://math.hws.edu/javanotes/
- *Think Java* (2nd ed.) — Chapter 7: Arrays: https://greenteapress.com/wp/think-java-2e/
- MIT OCW 6.092 — Assignment 3 covers array manipulation: https://ocw.mit.edu/courses/6-092-introduction-to-programming-in-java-january-iap-2010/
