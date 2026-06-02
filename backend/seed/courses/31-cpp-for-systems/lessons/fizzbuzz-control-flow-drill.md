# Exercise: Branching and Loop Logic from stdin

This exercise tests your ability to combine the control-flow constructs from this module — `if`/`else`, `switch`, and loops — to solve a classic programming problem with a twist: the rules are driven by input, not hardcoded.

## What You'll Implement

You will read two integers `A` and `B` from stdin, then iterate from `1` to `N` (also from stdin), printing:

- `FizzBuzz` if the number is divisible by both A and B
- `Fizz` if divisible by A only
- `Buzz` if divisible by B only
- The number itself otherwise

Each value goes on its own line.

## Skills Practiced

- Reading multiple values from stdin in a loop
- Nested `if`/`else if`/`else` branching with modulo conditions
- Correctly ordering conditions (check combined case before individual cases)
- Loop bounds and off-by-one awareness

## Constraints and Tips

- `A`, `B`, and `N` are positive integers: `1 <= A, B <= 100`, `1 <= N <= 1000`.
- The combined divisibility check (`n % A == 0 && n % B == 0`) must come **first** in your condition chain — otherwise you will print `Fizz` or `Buzz` for numbers that should print `FizzBuzz`.
- There is no `switch` version of this problem — the modulo test is a range/boolean expression, which belongs in an `if`/`else` chain.

## Sample Run

**Input:**
```
3 5 15
```

**Output:**
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
```

Open the problem and implement a solution. The judge will test your solution against several cases including non-standard values of A and B.
