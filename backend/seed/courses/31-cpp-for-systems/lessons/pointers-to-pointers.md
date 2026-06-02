# Pointers to Pointers and Double Indirection

A pointer stores an address. A pointer-to-pointer stores the address of a pointer. This is called **double indirection** and shows up in dynamic 2D arrays, command-line argument lists (`char** argv`), and functions that need to modify a pointer in the caller's scope.

## Declaration and Dereferencing

```cpp
int   value = 42;
int*  p  = &value;   // p  points to value
int** pp = &p;       // pp points to p
```

Each `*` in the declaration adds one level of indirection:

```cpp
std::cout << value  << "\n";   // 42   — the int itself
std::cout << *p     << "\n";   // 42   — one dereference
std::cout << **pp   << "\n";   // 42   — two dereferences
std::cout << *pp    << "\n";   // address of value (same as p)
std::cout << pp     << "\n";   // address of p
```

Dereference twice to get to the original value; dereference once to get the intermediate pointer.

## Memory Layout

```
pp  ──► [ address of p  ]   (8 bytes)
         │
         ▼
p   ──► [ address of value ] (8 bytes)
         │
         ▼
value ► [ 42 ]               (4 bytes)
```

## Use Case 1: Modify a Pointer From a Function

A function can only modify the caller's variable if it receives a pointer to it. To modify a pointer, pass a pointer-to-pointer:

```cpp
#include <cstdlib>

void allocate(int** pp, int count) {
    *pp = (int*)malloc(sizeof(int) * count);  // modify caller's pointer
}

int main() {
    int* data = nullptr;
    allocate(&data, 10);     // pass address of data
    data[0] = 1;
    free(data);
}
```

Without `int**` the function would only change its local copy of the pointer.

## Use Case 2: `char** argv` in `main`

```cpp
int main(int argc, char** argv) {
    // argv[0] is the program name
    // argv[i] is a char* pointing to the i-th argument string
    for (int i = 0; i < argc; i++)
        std::cout << argv[i] << "\n";
}
```

`char**` is a pointer to the first element of an array of `char*` pointers. Each `char*` itself points to a null-terminated string. Three levels of data: the array, the pointers, the character bytes.

## Use Case 3: Dynamic 2D Arrays

```cpp
int rows = 3, cols = 4;

// Allocate array of row-pointers
int** matrix = new int*[rows];
for (int i = 0; i < rows; i++)
    matrix[i] = new int[cols];   // each row is its own allocation

matrix[1][2] = 99;   // row 1, column 2

// Deallocate in reverse order
for (int i = 0; i < rows; i++)
    delete[] matrix[i];
delete[] matrix;
```

Each `matrix[i]` is an `int*`; `matrix` itself is `int**`.

## Triple Indirection (and Beyond)

The pattern extends: `int*** ppp` is a pointer to a pointer to a pointer to an int. In practice, code with more than two levels of indirection is hard to read and usually signals that a different data structure (a struct, a class, a flat array) would be cleaner.

## Worked Example: Singly-Linked List Head Reassignment

```cpp
struct Node { int val; Node* next; };

void prepend(Node** head, int val) {
    Node* n = new Node{val, *head};
    *head = n;   // modify caller's head pointer
}

int main() {
    Node* head = nullptr;
    prepend(&head, 3);
    prepend(&head, 2);
    prepend(&head, 1);
    // list: 1 -> 2 -> 3
    for (Node* cur = head; cur; cur = cur->next)
        std::cout << cur->val << " ";
}
```

If `prepend` received `Node*` instead of `Node**`, setting `*head` inside would be useless — it would only change the local copy.

## Common Pitfalls

- **Off-by-one dereference**: using `*pp` when you meant `**pp` writes to the pointer, not the value.
- **Freeing in the wrong order** in a 2D array: deleting the array of pointers first leaves the row arrays leaked.
- **NULL at any level**: both the outer pointer and any inner pointer can independently be null; check each level before dereferencing.

> **Interview answer:** A pointer-to-pointer (`T**`) stores the address of a pointer. Dereference once to get the inner pointer, twice to reach the final data. It is used when a function must modify the caller's pointer (e.g., `allocate`), for `char** argv`, and for ragged 2D arrays.
