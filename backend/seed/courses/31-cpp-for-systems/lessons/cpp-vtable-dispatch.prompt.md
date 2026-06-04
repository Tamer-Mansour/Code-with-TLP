# Virtual Dispatch Table Lookup

## Problem Description

Simulate C++ virtual dispatch (vtable lookup). Given a class hierarchy, method definitions, object instances, and a series of method calls, resolve each call to the correct override by walking up the inheritance chain from the most-derived class.

## Input Format

```
N
CLASS name1 [parent1]
CLASS name2 [parent2]
...
M
METHOD class_name method_name return_value
...
K
OBJECT obj_name class_name
...
Q
CALL obj_name method_name
...
```

- **N** class definitions. `CLASS name` is a base class (no parent). `CLASS name parent` inherits from `parent`.
- **M** method definitions. `METHOD cls meth val` means class `cls` defines (or overrides) `meth` with return value `val`.
- **K** object declarations. `OBJECT obj cls` creates object `obj` of type `cls`.
- **Q** calls. `CALL obj meth` — look up `meth` starting from `obj`'s class, walking up the chain. Print the return value of the first override found, or `ERROR` if none exists in the hierarchy.

## Constraints

- All names are uppercase letters only, length 1–20.
- Inheritance is single (no multiple inheritance).
- No cycles in the inheritance graph.
- N, M, K, Q ≤ 50 each.
- `OBJECT` and `CALL` only reference classes and objects that have been defined.

## Sample Input 1

```
3
CLASS Animal
CLASS Dog Animal
CLASS Poodle Dog
4
METHOD Animal speak Grunt
METHOD Dog speak Woof
METHOD Animal breathe Inhale
METHOD Poodle groom Fluff
3
OBJECT a Animal
OBJECT d Dog
OBJECT p Poodle
5
CALL a speak
CALL d speak
CALL p speak
CALL p breathe
CALL p groom
```

## Sample Output 1

```
Grunt
Woof
Woof
Inhale
Fluff
```

**Explanation:** `p.speak()` resolves to Dog's override (Woof) because Poodle does not override `speak`. `p.breathe()` walks to Animal (Inhale). `p.groom()` is defined directly on Poodle (Fluff).

## Sample Input 2

```
2
CLASS Shape
CLASS Circle Shape
3
METHOD Shape area Zero
METHOD Shape describe ShapeObj
METHOD Circle area PiRsq
2
OBJECT s Shape
OBJECT c Circle
4
CALL s area
CALL c area
CALL c describe
CALL c missing
```

## Sample Output 2

```
Zero
PiRsq
ShapeObj
ERROR
```

## Sample Input 3

```
4
CLASS A
CLASS B A
CLASS C B
CLASS D C
2
METHOD A run Go
METHOD C run Fast
3
OBJECT x A
OBJECT y B
OBJECT z D
3
CALL x run
CALL y run
CALL z run
```

## Sample Output 3

```
Go
Go
Fast
```

**Explanation:** `z` is of type D. Walking up: D has no `run`, C has `run = Fast` — stop. `y` is of type B. Walking up: B has no `run`, A has `run = Go` — stop.
