# Microservices (System Design view)

> See also `backend/microservices` for the code-level module.

## Monolith vs microservices
- **Monolith** — one deployable. Simple to build/test/deploy early; can become a big ball of mud.
- **Microservices** — independently deployable services around business capabilities.
  Team autonomy and independent scaling, at the cost of distributed-systems complexity.
- **Start with a modular monolith**; extract services when boundaries and pain are clear.

## Decomposition
- Around **bounded contexts** (DDD), not technical layers.
- Each service owns its **data** (no shared database).

## Communication
- **Synchronous** — REST/gRPC. Simple, but creates temporal coupling.
- **Asynchronous** — events/messaging. Looser coupling, eventual consistency.

## Cross-cutting concerns
- **API gateway** — single entry, routing, auth, rate limiting.
- **Service discovery** — find instances dynamically.
- **Configuration** — centralized, environment-aware.
- **Resilience** — timeouts, retries, circuit breakers, bulkheads.
- **Observability** — logs, metrics, distributed tracing (correlation IDs).

## Data management
- **Database per service**.
- **Saga** for cross-service transactions (choreography vs orchestration).
- **Outbox pattern** for reliable event publishing.
- **CQRS** for read/write separation.

## Deployment
- Containers + orchestration (Kubernetes), independent CI/CD pipelines.

## Trade-offs
- **Team autonomy & independent scaling** vs **operational + distributed complexity**.
- **Independent deploys** vs **harder end-to-end testing and debugging**.
- **Polyglot freedom** vs **consistency and shared tooling costs**.
- Microservices are an **organizational** tool as much as a technical one (Conway's Law).
