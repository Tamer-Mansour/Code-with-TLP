# Overloading [], (), and Function Objects

The subscript operator `[]` and call operator `()` are two of the most powerful overloads. Both must be member functions. Overloading `()` creates **function objects** (functors), the foundation of STL predicates and lambdas.

## The Subscript Operator `[]`

Provide both a `const` and a non-const overload so the object works in read and write contexts:

```cpp
class IntArray {
    int* data;
    size_t size_;
public:
    IntArray(size_t n) : data(new int[n]()), size_(n) {}
    ~IntArray() { delete[] data; }

    // Non-const: allows writing — arr[2] = 42;
    int& operator[](size_t i) {
        if (i >= size_) throw std::out_of_range("index out of range");
        return data[i];
    }

    // Const: read-only access
    const int& operator[](size_t i) const {
        if (i >= size_) throw std::out_of_range("index out of range");
        return data[i];
    }
};

IntArray arr(5);
arr[2] = 99;              // calls non-const, returns int&
const IntArray& ref = arr;
int v = ref[2];           // calls const, returns const int&
```

### C++23: Multi-Dimensional `[]`

C++23 allows multiple arguments to `[]`:

```cpp
// C++23 only
T& operator[](size_t row, size_t col) { return data[row * cols + col]; }
mat[1, 2] = 5;  // cleaner than mat(1, 2) for matrices
```

Before C++23, use `operator()` for multi-dimensional indexing.

## The Call Operator `()`

Overloading `()` makes objects **callable** — they behave like functions but carry state:

```cpp
struct Adder {
    int value;
    explicit Adder(int v) : value(v) {}

    int operator()(int x) const { return x + value; }
};

Adder add5{5};
int result = add5(10);   // calls add5.operator()(10) == 15
```

Functors are preferred over raw function pointers when state is needed, because:

- They can be inlined by the compiler.
- They carry context without global variables.
- They work with STL algorithms.

## STL Predicates and Comparators

```cpp
#include <algorithm>
#include <vector>

struct GreaterThan {
    int threshold;
    explicit GreaterThan(int t) : threshold(t) {}
    bool operator()(int x) const { return x > threshold; }
};

std::vector<int> v = {1, 8, 3, 9, 2, 7};
auto it = std::find_if(v.begin(), v.end(), GreaterThan{6});
// *it == 8
```

This is exactly what a lambda `[threshold](int x){ return x > threshold; }` compiles to internally.

## Callable with Multiple Overloads

`operator()` can be overloaded for different argument types:

```cpp
struct Logger {
    void operator()(const std::string& msg) const {
        std::cout << "[INFO] " << msg << '\n';
    }
    void operator()(int code, const std::string& msg) const {
        std::cout << "[" << code << "] " << msg << '\n';
    }
};

Logger log;
log("Hello");          // [INFO] Hello
log(404, "Not found"); // [404] Not found
```

## Worked Example: Memoised Function Object

```cpp
#include <unordered_map>

struct MemoFib {
    std::unordered_map<int, long long> cache;

    long long operator()(int n) {
        if (n <= 1) return n;
        auto it = cache.find(n);
        if (it != cache.end()) return it->second;
        return cache[n] = (*this)(n-1) + (*this)(n-2);
    }
};

MemoFib fib;
std::cout << fib(40);  // fast — results cached across calls
```

Stateful computation like this is impossible with a plain function pointer.

## Common Pitfalls

- **Missing `const` on query `[]`:** a `const` container cannot be indexed.
- **Returning by value from `[]`:** breaks assignment `arr[i] = x;` — must return a reference.
- **Making `[]` non-member:** the language requires it to be a member function.

> **Interview answer:** `operator[]` must be a member and should provide both `const` and non-const overloads returning references to support read and write access. `operator()` creates a functor — a callable object that carries state — and is the mechanism behind STL predicates and, internally, lambdas.
