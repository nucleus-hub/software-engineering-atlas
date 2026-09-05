# Messaging

## Why async messaging
Decouple producers from consumers, absorb spikes (load leveling), enable
event-driven architectures, and improve resilience.

## Queues vs logs vs pub/sub
- **Message queue** (RabbitMQ, SQS) — work distribution; a message is typically consumed once.
- **Log-based streaming** (Kafka) — append-only log; multiple consumers read at their own offset; replayable.
- **Pub/Sub** — fan-out to many subscribers.

## Delivery semantics
- **At-most-once** — may lose messages, never duplicates.
- **At-least-once** — never loses, may duplicate -> **consumers must be idempotent**.
- **Exactly-once** — hardest; often "effectively once" via idempotency + dedup.

## Ordering
- Global ordering is expensive. Kafka guarantees order **within a partition**.
- Use a partition key to keep related events ordered.

## Key concerns
- **Backpressure** — slow consumers; buffer, throttle, or shed load.
- **Dead-letter queues (DLQ)** — park poison messages for inspection.
- **Consumer groups** — scale consumption horizontally.
- **Schema evolution** — use a schema registry; keep changes compatible.

## Patterns
- **Event-driven architecture**, **event sourcing**, **CQRS**, **outbox pattern**
  (reliably publish events with DB writes), **saga** (distributed transactions).

## Trade-offs
- **Decoupling & resilience** vs **added infra + eventual consistency + debugging complexity**.
- **At-least-once** simplicity vs the burden of **idempotent consumers**.
- **Strong ordering** vs **throughput/partitioning**.
- **Queue** (simple, consume-once) vs **log** (replayable, multi-consumer, more ops).
