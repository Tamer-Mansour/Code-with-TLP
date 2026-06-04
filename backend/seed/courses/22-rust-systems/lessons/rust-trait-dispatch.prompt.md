# Trait Dispatch Resolver

Given a set of type-trait implementation declarations and a list of dispatch calls, determine what method will be called or whether an error occurs.

## Input Format

```
T
<Type> implements <Trait>
<Type> implements <Trait>
...  (T lines)
C
<dispatch call>
<dispatch call>
...  (C lines)
```

Each dispatch call is one of:

- `STATIC <Trait> <Type>` — static (generic) dispatch: the compiler resolves `<Type>` to a specific implementation
- `DYNAMIC <Trait> <Type1>,<Type2>,...` — dynamic (`dyn Trait`) dispatch: checks all types in the comma-separated list

## Output

For each dispatch call, print one line:

- `STATIC`: print `<Type>::<Trait>_method` if the type implements the trait, or `ERROR: <Type> does not implement <Trait>` if not.
- `DYNAMIC`: print `OK: dyn <Trait>` if all listed types implement the trait, or `ERROR: <TypeN> does not implement <Trait>` for the first failing type.

## Sample Input

```
5
Dog implements Animal
Cat implements Animal
Dog implements Pet
Fish implements Animal
Robot implements Machine
6
STATIC Animal Dog
STATIC Animal Cat
STATIC Pet Fish
DYNAMIC Animal Dog,Cat,Fish
DYNAMIC Pet Dog,Cat
STATIC Machine Robot
```

## Sample Output

```
Dog::Animal_method
Cat::Animal_method
ERROR: Fish does not implement Pet
OK: dyn Animal
ERROR: Cat does not implement Pet
Robot::Machine_method
```

## Constraints

- `1 <= T <= 50` type-trait implementations
- `1 <= C <= 50` dispatch calls
- Type and trait names are single words with no spaces
- For DYNAMIC calls, types are comma-separated with no spaces
