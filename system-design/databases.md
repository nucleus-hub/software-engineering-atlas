# Databases

## SQL vs NoSQL
- **SQL (relational)** — strong schema, ACID, joins, great for complex queries and integrity.
- **NoSQL** families:
  - **Document** (MongoDB) — flexible schema, nested data.
  - **Key-value** (Redis, DynamoDB) — fast lookups, simple model.
  - **Wide-column** (Cassandra) — huge write throughput, tunable consistency.
  - **Graph** (Neo4j) — relationship-heavy queries.

## ACID vs BASE
- **ACID** — Atomicity, Consistency, Isolation, Durability.
- **BASE** — Basically Available, Soft state, Eventual consistency.

## Transactions & isolation levels
Read Uncommitted -> Read Committed -> Repeatable Read -> Serializable.
Anomalies to know: dirty read, non-repeatable read, phantom read.

## Indexing
- B-tree (range + equality), hash (equality), composite indexes, covering indexes.
- Indexes speed reads, slow writes, and use space. Index for real query patterns.

## Normalization vs denormalization
- **Normalize** to reduce redundancy and anomalies.
- **Denormalize** for read performance (fewer joins), accepting update complexity.

## Scaling databases
- **Replication** (read scaling, HA)
- **Partitioning/sharding** (write scaling)
- **Connection pooling**
- **Read/write splitting**, **CQRS** for heavy read workloads

## Migrations
Use **Flyway** or **Liquibase**. Prefer backward-compatible, expand/contract migrations.

## Trade-offs
- **SQL** integrity & querying vs **NoSQL** flexibility & horizontal scale.
- **Normalization** (write-friendly, clean) vs **denormalization** (read-fast, redundant).
- **Strong isolation** correctness vs concurrency/throughput.
- **More indexes** faster reads vs slower writes + storage.
