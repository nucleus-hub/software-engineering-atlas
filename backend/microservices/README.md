# Microservices

Patterns and building blocks for service-oriented / microservice architectures.

## Topics
- Service decomposition & bounded contexts
- Synchronous communication (REST clients, `RestClient`/`WebClient`)
- Resilience: timeouts, retries, circuit breakers, bulkheads
- Configuration and service discovery concepts
- Observability with Actuator + Micrometer
- API gateway and edge concerns (conceptual + examples)

## Run / Test
```bash
mvn -pl backend/microservices -am test
```

## Status
Skeleton. Consider multiple small apps (e.g. `order-service`, `inventory-service`) as sub-packages or future modules.
