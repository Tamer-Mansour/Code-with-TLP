# Sum and Average

A C++ STL one-liner:

```cpp
int total = std::accumulate(v.begin(), v.end(), 0);
double avg = static_cast<double>(total) / v.size();
```

In this exercise (in Python) you'll read N integers and print both their sum and their average.

See the prompt for the exact contract.
