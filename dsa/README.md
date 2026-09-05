# Data Structures and Algorithms (DSA)

Executable **Java** implementations, each paired with a problem description,
approach(es), complexity analysis, and **JUnit 5 tests**.

## Suggested layout

```
dsa/
├── src/main/java/dev/atlas/dsa/
│   ├── arrays/
│   ├── strings/
│   ├── linkedlists/
│   ├── stacksqueues/
│   ├── trees/
│   ├── graphs/
│   ├── heaps/
│   ├── hashing/
│   ├── searching/
│   ├── sorting/
│   ├── recursion/
│   ├── backtracking/
│   ├── greedy/
│   └── dp/               # dynamic programming
└── src/test/java/dev/atlas/dsa/...   # mirror the package structure
```

## Each problem should include
1. **Problem statement** (link + restatement)
2. **Approach(es)** — brute force -> optimized
3. **Complexity** — time & space (Big-O)
4. **Implementation** — clean, tested Java
5. **Tests** — edge cases included

See [`PROBLEM_TEMPLATE.md`](PROBLEM_TEMPLATE.md) for a consistent format.

## Run / Test
```bash
mvn -pl dsa -am test
```

## Status
Skeleton. Add packages + tests as you solve problems.
