# Disk Scheduling: SCAN Algorithm

## Problem Description

Simulate the **SCAN** (elevator) disk scheduling algorithm. Given the initial head position, initial direction, and a list of pending track requests, compute the order in which requests are serviced and the total head movement in tracks.

### Rules

- The disk has tracks numbered **0 to 199** (inclusive).
- Direction `up` means the head moves toward higher track numbers.
- Direction `down` means the head moves toward lower track numbers.
- The head services all pending requests it encounters along the current direction.
- After servicing all requests in the current direction, the head travels to the boundary (track 199 if going up, track 0 if going down), then reverses and services remaining requests.
- Service order follows the head movement order.

## Input Format

```
Line 1: head direction    (integer head position and 'up' or 'down')
Line 2: space-separated track requests  (integers)
```

## Output Format

```
Service order: <r1> <r2> ...
Total head movement: <integer>
```

## Constraints

- `0 <= head <= 199`
- Direction is exactly `up` or `down`.
- `1 <= number of requests <= 20`
- `0 <= request <= 199`
- No request equals the initial head position.
- All requests are distinct.

## Sample Input 1

```
53 up
98 183 37 122 14 124 65 67
```

## Sample Output 1

```
Service order: 65 67 98 122 124 183 37 14
Total head movement: 331
```

*(Head moves 53→199 (servicing 65,67,98,122,124,183), then 199→14 (servicing 37,14).)*

## Sample Input 2

```
50 down
176 79 34 60 92 11 41 114
```

## Sample Output 2

```
Service order: 41 34 11 60 79 92 114 176
Total head movement: 226
```

## Sample Input 3

```
100 up
50 150
```

## Sample Output 3

```
Service order: 150 50
Total head movement: 248
```

*(Head moves 100→150→199 (boundary) then 199→50. Movement = 50 + 49 + 149 = 248.)*

## Notes for Implementers

- Split requests into two groups: those `>= head` (right group) and those `< head` (left group).
- For direction `up`: service the right group in ascending order, then travel to track 199, then service the left group in **descending** order.
- For direction `down`: service the left group in descending order, then travel to track 0, then service the right group in **ascending** order.
- Count all head movement including the trip to the boundary, even if no requests are there.
