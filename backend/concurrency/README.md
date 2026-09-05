# Concurrency

Concurrent and parallel programming in Java 21.

## Topics
- Threads, `Runnable`/`Callable`, the memory model
- `ExecutorService`, thread pools, and sizing
- **Virtual threads** (Project Loom, Java 21) vs platform threads
- Synchronization: `synchronized`, `Lock`, `ReadWriteLock`, atomics
- `CompletableFuture` and async composition
- Concurrent collections & common pitfalls (race conditions, deadlock, livelock)
- Structured concurrency (preview) overview

## Run / Test
```bash
mvn -pl backend/concurrency -am test
```

## Status
Skeleton. Great place for small, self-contained demos that print thread behavior.
