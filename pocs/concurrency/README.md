# POC: Concurrency

Hands-on experiments to feel concurrency behavior (distinct from the
`backend/concurrency` learning module, which is more tutorial-style).

## Goals
- Simulate load and contention
- Compare platform threads vs virtual threads (Java 21) under load
- Reproduce race conditions, then fix them
- Benchmark thread-pool sizing

## Run (planned)
```bash
mvn -pl pocs/concurrency -am exec:java   # or a small main-based runner
```

## Status
Skeleton.
