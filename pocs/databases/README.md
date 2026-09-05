# POC: Databases

Demonstrates relational persistence concepts with JPA/Hibernate.

## Goals
- Entities, relationships, and the persistence context
- Transactions and isolation levels
- Indexing and query performance
- Schema migrations (Flyway/Liquibase, added later)
- H2 for quick local runs; PostgreSQL via Docker for realism

## Run (planned)
```bash
mvn -pl pocs/databases -am spring-boot:run    # uses H2 by default
```

## Status
Skeleton.
