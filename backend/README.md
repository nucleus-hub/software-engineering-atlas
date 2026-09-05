# Backend

Java 21 + Spring Boot 3.3.x backend learning modules, built with Maven (multi-module).

## Modules

| Module               | Focus |
|----------------------|-------|
| `spring-fundamentals`| IoC/DI, configuration, beans, profiles, Spring Boot basics |
| `rest-apis`          | RESTful API design, controllers, validation, error handling, versioning |
| `microservices`      | Service decomposition, communication, resilience, config, discovery |
| `concurrency`        | Threads, executors, virtual threads (Java 21), synchronization, CompletableFuture |
| `design-patterns`    | GoF and enterprise patterns with runnable Java examples |

## Build

From the repository root:
```bash
mvn -pl backend -am clean install
```

Or build a single module:
```bash
mvn -pl backend/rest-apis -am clean install
```

## Status
Skeleton in place. Each submodule README describes intended content; code samples land incrementally.
