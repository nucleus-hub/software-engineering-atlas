# Proof of Concepts (POCs)

Independent, runnable experiments. Each POC is self-contained and documents
**what it demonstrates**, **how to run it**, and **what to observe**.

## Maven POC modules (part of the aggregate build)

| POC             | Demonstrates |
|-----------------|--------------|
| `kafka`         | Producing/consuming, topics, consumer groups, delivery semantics |
| `redis`         | Caching, data structures, TTL, pub/sub |
| `databases`     | JPA/Hibernate, transactions, indexing, migrations |
| `authentication`| Spring Security, JWT, sessions, RBAC |
| `caching`       | Spring Cache abstraction, cache-aside, eviction |
| `concurrency`   | Parallelism experiments, virtual threads, load simulation |

## Documentation-first POCs (standalone projects added later)

| POC                   | Notes |
|-----------------------|-------|
| `distributed-systems` | Consensus, replication, partitioning demos (may span multiple runtimes) |
| `cloud`               | Cloud concepts: object storage, queues, serverless (provider-specific) |

These live as README-only folders for now and will be promoted to real modules/projects as they take shape.

## Running a POC
Most POCs require external services (Kafka, Redis, a DB). Docker Compose files will be
added per-POC when code lands. For Java POCs in the aggregate build:
```bash
mvn -pl pocs/<name> -am spring-boot:run
```

## Status
Skeleton. Each POC README describes intent and planned run steps.
