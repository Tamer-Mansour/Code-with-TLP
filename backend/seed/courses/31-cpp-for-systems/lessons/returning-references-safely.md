# Returning References: Safe and Dangerous Cases

Returning a reference from a function is powerful — it avoids copying and enables assignment through a function call (the basis of `operator[]`). But return a reference to the wrong thing and you have a dangling reference: undefined behavior that may silently corrupt memory or crash far from the bug.

## When Returning a Reference Is Safe

A returned reference is safe if and only if the referenced object **outlives the function call**. Three common safe cases:

### 1. Returning a Reference to a Parameter

If the caller passes an object and the function returns a reference to it, the object's lifetime is controlled by the caller — always valid:

```cpp
const std::string& longer(const std::string& a, const std::string& b) {
    return a.size() >= b.size() ? a : b;
}

int main() {
    std::string x = "hello", y = "world!";
    const std::string& result = longer(x, y);
    std::cout << result;  // "world!" — safe, x and y are still alive
}
```

### 2. Returning a Reference to a Member (via `this`)

Member functions commonly return `*this` or a member field by reference:

```cpp
class Buffer {
    std::vector<char> data_;
public:
    std::vector<char>& data() { return data_; }          // mutable
    const std::vector<char>& data() const { return data_; } // const
    Buffer& append(char c) { data_.push_back(c); return *this; }  // chaining
};
```

The member lives as long as the `Buffer` object does. As long as the caller keeps the `Buffer` alive, the returned reference is valid.

### 3. Returning a Reference to a Static or Global

```cpp
const std::string& emptyString() {
    static const std::string s;
    return s;  // static — lives forever
}
```

## When Returning a Reference Is Dangerous

### Returning a Reference to a Local Variable

This is the classic mistake. The local is destroyed when the function returns:

```cpp
int& badRef() {
    int local = 42;
    return local;   // local destroyed here — dangling reference!
}

int main() {
    int& r = badRef();
    std::cout << r;  // undefined behavior
}
```

Most compilers warn about this (`-Wreturn-local-addr` in GCC/Clang). Heed the warning.

### Storing a Reference from `longer()` After the Parameters Die

The `longer()` example above is safe *only* while `x` and `y` are alive. Storing the reference beyond their scope is dangerous:

```cpp
const std::string* danger() {
    std::string a = "short", b = "longer string";
    const std::string& ref = longer(a, b);
    return &ref;  // a and b destroyed here — dangling pointer to stack!
}
```

### Returning a Reference to a Temporary

```cpp
const int& bad() {
    return 5 + 3;  // temporary int — destroyed at semicolon
}
```

The compiler may warn, but the behavior is undefined.

## operator[] Pattern

The most common legitimate use of returning a non-const reference is container element access:

```cpp
class IntArray {
    int data_[100];
public:
    int& operator[](int i)       { return data_[i]; }
    const int& operator[](int i) const { return data_[i]; }
};

IntArray arr;
arr[0] = 42;   // operator[] returns a reference; assignment writes through it
```

Both overloads are safe because `data_` is a member of `arr`, which outlives the expression.

## Worked Example: Builder Pattern with Reference Return

```cpp
class QueryBuilder {
    std::string query_;
public:
    QueryBuilder& select(const std::string& cols) {
        query_ += "SELECT " + cols + " ";
        return *this;
    }
    QueryBuilder& from(const std::string& table) {
        query_ += "FROM " + table;
        return *this;
    }
    std::string build() const { return query_; }
};

int main() {
    std::string q = QueryBuilder()
        .select("id, name")
        .from("users")
        .build();
    std::cout << q;  // SELECT id, name FROM users
}
```

Each method returns `*this` by reference — safe because the `QueryBuilder` object lives for the entire chained expression.

## Summary Rule

> A returned reference is safe if the referenced storage outlives the caller's use of that reference. When in doubt, return by value — modern compilers apply NRVO/RVO and the copy is often elided entirely.

> **Interview answer:** Returning a reference is safe when it refers to an object that outlives the function — such as a parameter, a member, or a static. Returning a reference to a local variable is always undefined behavior because the local is destroyed when the function returns.
