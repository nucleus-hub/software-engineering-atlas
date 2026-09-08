# System Design - Advanced

Advanced system design and low-level design (LLD) topics. Assumes you're
comfortable with [`../basics`](../basics/README.md). Check items off as you learn them.

---

## 1. LLD: Behavioral Design Patterns
- [ ] Strategy, Observer, Command, State
- [ ] Iterator, Mediator, Chain of Responsibility, Template Method

## 2. LLD: Real-World Machine Coding Case Studies
- [ ] E-commerce cart calculation engine
- [ ] Movie ticket booking system (BookMyShow)
- [ ] Parking lot tracker
- [ ] Ride-sharing dispatch model

## 3. Concurrency Control, Race Conditions & Locking
- [ ] **Failures:** race conditions, lost update, dirty reads, non-repeatable reads, phantom reads
- [ ] **Isolation levels:** Read Uncommitted, Read Committed, Repeatable Read, Serializable
- [ ] **Locking:** optimistic vs pessimistic
- [ ] **Atomic state:** CAS (compare-and-set), versioning patterns, distributed locks

## 4. Distributed Transactions & Consensus
- [ ] Two-Phase Commit (2PC)
- [ ] Saga pattern (orchestration vs choreography)
- [ ] Paxos / Raft consensus
- [ ] Distributed state machine replication

## 5. Advanced Replication, Quorums & Conflict Resolution
- [ ] Leader-based, multi-leader, and leaderless replication
- [ ] Replication lag, stale reads, and session guarantees
- [ ] Read/write quorums and tunable consistency
- [ ] Leader election, failover, split-brain, and fencing tokens
- [ ] Conflict resolution, read repair, hinted handoff, and anti-entropy
- [ ] Tombstones and deletion propagation

## 6. Event-Driven Systems & Message Queues
- [ ] **Kafka deep dive:** brokers, topics, partitions, offsets, log segments, controller node
- [ ] **Delivery & idempotency:** exactly-once vs at-least-once, producer & consumer idempotency
- [ ] **Reliability:** retries, acks (0/1/all), CDC, event sourcing, CQRS, Apache Flink
- [ ] **Ordering & scaling:** partition-key selection, consumer groups, rebalancing, competing consumers
- [ ] **Operations:** slow consumers, lag management, replay, retention, and schema registries
- [ ] **Transactions:** outbox/inbox patterns and transactional messaging
- [ ] **Error handling:** poison pills, circuit-breaking consumers, dead-letter topics (DLT)

## 7. Idempotency & Retries
- [ ] Designing idempotent API endpoints, unique idempotency keys
- [ ] Handling retry storms, deduplication layers

## 8. Distributed Caching & High-Concurrency Failures
- [ ] Cache stampede (thundering herd)
- [ ] Hot-key / big-key mitigation
- [ ] Cache penetration, cache avalanche, Bloom filters

## 9. Rate Limiting & Throttling
- [ ] **Algorithms:** fixed window, sliding window log, token bucket, leaky bucket
- [ ] **Scopes:** per-user vs per-IP vs per-API
- [ ] **Architecture:** distributed rate limiting (Redis token bucket, in-memory instances, gateway throttling)
- [ ] **Trade-offs:** accuracy (strict sync) vs performance/latency

## 10. Backpressure, Admission Control & Overload Protection
- [ ] Producer/consumer backpressure and bounded queues
- [ ] Load shedding, admission control, and concurrency limits
- [ ] Queue lag, saturation, and adaptive throttling
- [ ] Retry budgets and preventing retry amplification
- [ ] Tail latency and coordinated omission

## 11. Fault Tolerance, Resilience & Failure Handling
- [ ] **Strategies:** fail-fast vs graceful degradation, timeouts, retries with exponential backoff + jitter
- [ ] **Patterns:** circuit breakers, bulkheads, isolating partial failures, cascading failure prevention

## 12. Data Consistency & Clock Synchronization
- [ ] **CAP theorem:** consistency vs availability vs partition tolerance
- [ ] **PACELC theorem:** normal (latency vs consistency) vs partition state
- [ ] **Consistency models:** strong, eventual, read-your-writes, monotonic reads
- [ ] **Distributed clocks:** vector clocks, Lamport timestamps, TrueTime

## 13. Storage Types - Latency, Cost & Trade-offs
- [ ] **Physical:** NVMe SSDs vs HDDs, sequential vs random access
- [ ] **File-based:** network file systems, object storage (S3), distributed FS (HDFS)
- [ ] **Database:** block storage volumes, log-structured storage engines
- [ ] **Log/sequential:** append-only transaction logs, write-ahead logs (WAL)

## 14. Observability, Monitoring & Alerting
- [ ] **Pillars:** metrics vs logs vs traces
- [ ] **Frameworks:** RED (Rate, Errors, Duration), USE (Utilization, Saturation, Errors), 4 Golden Signals
- [ ] **Governance:** SLIs, SLOs, SLAs
- [ ] **Logistics:** distributed tracing (span propagation, trace contexts), alert fatigue, thresholds, OpenTelemetry, Jaeger, Prometheus, ELK

## 15. Single Region vs Multi-Region Deployment
- [ ] **Topologies:** single region active-only, active-passive, active-active
- [ ] **Metrics:** RPO vs RTO under different faults, split-brain handling, global traffic management

## 16. Data Migration & Zero-Downtime Evolution
- [ ] Expand-and-contract schema migrations and version skew
- [ ] Dual reads, dual writes, backfills, and validation
- [ ] Shadow traffic and CDC-based migrations
- [ ] Repartitioning and re-sharding live systems
- [ ] Rollback and reconciliation strategies

## 17. Disaster Recovery & Operational Readiness
- [ ] Backup strategies and regular restore testing
- [ ] Regional evacuation and dependency failure planning
- [ ] RPO/RTO-driven architecture and disaster recovery runbooks
- [ ] Game days, chaos engineering, and capacity headroom
- [ ] Incident response and blameless postmortems

## 18. Batch, Stream & Workflow Processing
- [ ] Batch vs stream processing
- [ ] Event time vs processing time; windows and watermarks
- [ ] Late and out-of-order events
- [ ] Stateful stream processing, checkpoints, and recovery
- [ ] Workflow orchestration; scheduled and long-running jobs
- [ ] Exactly-once claims and their practical boundaries

## 19. Multi-Tenancy, Isolation & Fairness
- [ ] Shared vs isolated tenant models
- [ ] Tenant-aware partitioning and data isolation
- [ ] Noisy-neighbor and hot-tenant mitigation
- [ ] Per-tenant quotas, rate limits, and fair resource allocation
- [ ] Cost attribution

## 20. Security, Privacy & Abuse Resistance
- [ ] Threat modeling and trust boundaries
- [ ] Least privilege and service-to-service identity
- [ ] Encryption, key management, and key rotation
- [ ] PII handling, retention, and audit trails
- [ ] Replay protection and request signing
- [ ] DDoS and abuse prevention

---

> Split any topic into its own `.md` file here as your notes grow (e.g. `kafka.md`).
