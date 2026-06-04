# Quiz: Control Flow and Iteration

Test your understanding of conditionals, loops, and loop control in Python.

---

**Question 1.** What does the `%` (modulo) operator return?

- [ ] The quotient of integer division
- [x] The remainder after integer division
- [ ] The exponent of a number
- [ ] The absolute value

---

**Question 2.** What is printed by the following code?

```python
for i in range(3):
    print(i)
```

- [ ] 1, 2, 3
- [x] 0, 1, 2
- [ ] 0, 1, 2, 3
- [ ] Nothing — range(3) is empty

---

**Question 3.** In a FizzBuzz solution, why must `n % 15 == 0` be checked BEFORE `n % 3 == 0`?

- [ ] Because 15 is larger than 3
- [x] Because if `n % 3 == 0` fires first, a multiple of 15 prints "Fizz" instead of "FizzBuzz"
- [ ] Python evaluates conditions in reverse order
- [ ] `elif` skips all remaining conditions once any is true

---

**Question 4.** What does `break` do inside a loop?

- [ ] Restarts the loop from the beginning
- [ ] Skips the current iteration and goes to the next
- [x] Exits the loop immediately
- [ ] Raises an error

---

**Question 5.** How many times does the inner loop body execute in total?

```python
for i in range(3):
    for j in range(4):
        print(i, j)
```

- [ ] 3
- [ ] 4
- [ ] 7
- [x] 12

---

**Question 6.** What is the difference between `if` and `elif`?

- [ ] There is no difference — they are synonyms
- [x] Multiple `if` blocks each evaluate independently; `elif` only evaluates if all preceding conditions were False
- [ ] `elif` can only be used with `while` loops
- [ ] `if` is for numbers; `elif` is for strings

---

**Question 7.** What does `continue` do?

- [ ] Exits the current loop
- [ ] Breaks out of a nested loop
- [x] Skips the remaining code in the current iteration and moves to the next iteration
- [ ] Jumps to the next function call

---

**Question 8.** What is printed?

```python
x = 10
while x > 0:
    x -= 3
    if x == 1:
        break
print(x)
```

- [ ] 10
- [x] 1
- [ ] -2
- [ ] 0
