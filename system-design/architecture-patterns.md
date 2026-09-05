# Architecture Patterns

## Application architecture
- **Layered (n-tier)** — presentation / business / data. Simple, familiar; risk of anemic layers.
- **Hexagonal (ports & adapters)** — domain at the center, I/O at the edges. Highly testable.
- **Clean / Onion** — dependencies point inward toward the domain.
- **Modular monolith** — clear internal module boundaries in one deployable.

## Domain modeling
- **Domain-Driven Design (DDD)** — bounded contexts, aggregates, ubiquitous language.

## Data & flow patterns
- **CQRS** — separate read and write models.
- **Event Sourcing** — store state as a sequence of events.
- **Event-Driven Architecture** — components react to events.
- **Saga** — long-running distributed transactions.
- **Outbox** — reliable event publication alongside DB writes.

## Integration patterns
- **API Gateway**, **Backend for Frontend (BFF)**, **Strangler Fig** (incremental migration),
  **Sidecar**, **Anti-Corruption Layer**.

## Deployment patterns
- **Blue-green**, **canary**, **rolling** deployments.
- **Feature flags** for decoupling deploy from release.

## Reliability patterns
- **Circuit breaker**, **retry with backoff**, **bulkhead**, **rate limiting**,
  **timeout**, **fallback / graceful degradation**.

## Trade-offs
- **Layered** simplicity vs **hexagonal/clean** testability & indirection cost.
- **Event sourcing** auditability/flexibility vs complexity and read-model rebuilds.
- **CQRS** read/write scaling vs two models to maintain and eventual consistency.
- Every pattern is a tool: apply where the pain justifies it (avoid pattern cargo-culting).
