# Proof of Concepts (POCs)

Independent, runnable experiments. Each POC is self-contained and documents
**what it demonstrates**, **how to run it**, and **what to observe**.

## Modules (part of the aggregate build)

| POC        | Demonstrates |
|------------|--------------|
| `caching`  | Spring Cache abstraction, cache-aside, eviction |
| `kafka`    | Producing/consuming, topics, consumer groups, delivery semantics |
| `redis`    | Caching, data structures, TTL, pub/sub |
| `spark`    | Distributed data processing, RDD/DataFrame APIs, Spark SQL |

## Running a POC
Most POCs require external services (Kafka, Redis) or a runtime (Spark).
Docker Compose files will be added per-POC when code lands. For the
Spring-based POCs in the aggregate build:
```bash
mvn -pl pocs/<name> -am spring-boot:run
```
For Spark:
```bash
mvn -pl pocs/spark -am package
```

## Status
Skeleton. Each POC README describes intent and planned run steps.
