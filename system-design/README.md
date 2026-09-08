# System Design

A structured curriculum for learning system design and low-level design (LLD),
split into two tiers. Work through **Basics** first, then **Advanced**. Check items
off as you master them.

## Basics

Foundational topics for designing scalable, reliable single-region systems and
structuring system design interviews.

### 1. System Design Interview Framework & Capacity Estimation
- [ ] Functional vs non-functional requirements
- [ ] Constraints, assumptions, scope control, and identifying core use cases
- [ ] Read/write QPS, peak traffic, storage, bandwidth, and memory estimation
- [ ] Latency, availability, durability, and consistency targets
- [ ] High-level design, bottleneck analysis, and selecting deep dives
- [ ] Back-of-the-envelope calculations and validating estimates

### 2. LLD: Object-Oriented Principles & Clean Code
- [ ] **SOLID principles** (simple explanations + examples):
  - Single Responsibility
  - Open/Closed
  - Liskov Substitution
  - Interface Segregation
  - Dependency Inversion
- [ ] **Clean code fundamentals:** DRY, KISS, YAGNI
- [ ] Encapsulation, polymorphism, composition vs inheritance

### 3. LLD: Creational & Structural Design Patterns
- [ ] **Creational:** Singleton, Factory Method, Abstract Factory, Builder, Prototype
- [ ] **Structural:** Adapter, Decorator, Facade, Proxy

### 4. Networking & Request Lifecycle
- [ ] DNS resolution, caching, and common failure modes
- [ ] TCP vs UDP; TLS termination and HTTPS
- [ ] HTTP/1.1 vs HTTP/2 vs HTTP/3
- [ ] Connection pooling, keep-alive, and timeout budgets
- [ ] Request path: client → DNS/CDN → load balancer → service → database
- [ ] Latency sources and network failure modes

### 5. Architecture Styles & Service Decomposition
- [ ] Layered architecture and modular monoliths vs microservices
- [ ] Stateless vs stateful services
- [ ] Service boundaries, ownership, and bounded contexts
- [ ] Shared database vs database per service
- [ ] Service discovery and configuration management

### 6. API Correctness, Security & Resource Design
- [ ] Resource-oriented API design; pagination, filtering, sorting, and partial updates
- [ ] Authentication vs authorization; sessions, cookies, OAuth 2.0, OIDC, and JWT trade-offs
- [ ] Request validation, standardized errors, timeouts, and request-size limits
- [ ] Secrets handling and encryption in transit and at rest

### 7. API Design & Service Communication
- [ ] **Protocols & paradigms:** REST vs gRPC vs GraphQL
- [ ] WebSockets, long polling, Server-Sent Events (SSE)
- [ ] **Lifecycle:** synchronous vs asynchronous communication
- [ ] Versioning strategies, backward compatibility, schema evolution

### 8. Load Balancing & Proxying
- [ ] **Types:** Layer 4 (transport), Layer 7 (application), DNS-based
- [ ] **Infrastructure:** proxies, reverse proxies, Anycast routing, Envoy, Nginx
- [ ] **Strategies:** round-robin, least connections, IP hash, weighted

### 9. Caching Core
- [ ] **Types:** client-side (browser), CDN, reverse proxy, application, distributed
- [ ] **Strategies:** write-through, write-around, write-back, cache-aside
- [ ] **Eviction policies:** LRU, LFU, FIFO, TTL-based

### 10. Database Fundamentals & Internal Architecture
- [ ] **ACID:** Atomicity, Consistency, Isolation, Durability
- [ ] **SQL vs NoSQL:** high-level trade-offs, when to choose which
- [ ] **NoSQL types:** key-value (Redis), document (MongoDB), wide-column (Cassandra), graph (Neo4j)
- [ ] **Storage & indexing:** B-Trees vs LSM-Trees, indexing trade-offs, read/write amplification
- [ ] **Schema design:** normalization (1NF, 2NF, 3NF) vs de-normalization

### 11. Practical Data Modeling & Query Design
- [ ] Model schemas from access patterns
- [ ] Primary, composite, secondary, and covering indexes
- [ ] Query plans, index selectivity, and avoiding unbounded scans
- [ ] One-to-many and many-to-many relationships
- [ ] Offset vs cursor/keyset pagination
- [ ] Partition-key and sort-key selection; avoiding N+1 queries

### 12. Data Partitioning, Sharding & Replication
- [ ] Horizontal vs vertical scaling, range-based partitioning, consistent hashing
- [ ] **Sharding execution:** SQL manual sharding (app-level routing, re-sharding) vs NoSQL native partitioning (hash keys)
- [ ] **Replication topologies:** master-slave, multi-master, peer-to-peer

### 13. Asynchronous Processing Basics
- [ ] Message queues, pub/sub mechanics
- [ ] Dead-letter queues (DLQ), message durability
- [ ] RabbitMQ, ActiveMQ

### 14. Availability & Deployment Fundamentals
- [ ] Health, liveness, and readiness checks
- [ ] Redundancy, failure domains, and removing single points of failure
- [ ] Stateless horizontal scaling and basic availability calculations
- [ ] Rolling, blue-green, and canary deployments
- [ ] Graceful shutdown and connection draining
- [ ] Backups and basic restore procedures

### 15. Distributed ID Generation
- [ ] Database sequences and allocation strategies
- [ ] UUID versions and their trade-offs
- [ ] ULID and other time-sortable identifiers
- [ ] Snowflake-style IDs
- [ ] Collision, ordering, predictability, and index-locality concerns

### 16. Threads, Thread Pools, Parallelization
- [ ] CPU-bound vs I/O-bound work and concurrency vs parallelism
- [ ] Little's Law, bounded queues, and thread-pool exhaustion
- [ ] **Java/Spring Boot:** thread pool config (TaskExecutor, Tomcat thread pools)
- [ ] **Optimization:** tuning core/max pool sizes, queue capacity limits, rejection policies

## Advanced

Advanced topics for reasoning about distributed failures, data consistency,
system evolution, overload, and operations at scale.

### 1. LLD: Behavioral Design Patterns
- [ ] Strategy, Observer, Command, State
- [ ] Iterator, Mediator, Chain of Responsibility, Template Method

### 2. LLD: Real-World Machine Coding Case Studies
- [ ] E-commerce cart calculation engine
- [ ] Movie ticket booking system (BookMyShow)
- [ ] Parking lot tracker
- [ ] Ride-sharing dispatch model

### 3. Concurrency Control, Race Conditions & Locking
- [ ] **Failures:** race conditions, lost update, dirty reads, non-repeatable reads, phantom reads
- [ ] **Isolation levels:** Read Uncommitted, Read Committed, Repeatable Read, Serializable
- [ ] **Locking:** optimistic vs pessimistic
- [ ] **Atomic state:** CAS (compare-and-set), versioning patterns, distributed locks

### 4. Distributed Transactions & Consensus
- [ ] Two-Phase Commit (2PC)
- [ ] Saga pattern (orchestration vs choreography)
- [ ] Paxos / Raft consensus
- [ ] Distributed state machine replication

### 5. Advanced Replication, Quorums & Conflict Resolution
- [ ] Leader-based, multi-leader, and leaderless replication
- [ ] Replication lag, stale reads, and session guarantees
- [ ] Read/write quorums and tunable consistency
- [ ] Leader election, failover, split-brain, and fencing tokens
- [ ] Conflict resolution, read repair, hinted handoff, and anti-entropy
- [ ] Tombstones and deletion propagation

### 6. Event-Driven Systems & Message Queues
- [ ] **Kafka deep dive:** brokers, topics, partitions, offsets, log segments, controller node
- [ ] **Delivery & idempotency:** exactly-once vs at-least-once, producer & consumer idempotency
- [ ] **Reliability:** retries, acks (0/1/all), CDC, event sourcing, CQRS, Apache Flink
- [ ] **Ordering & scaling:** partition-key selection, consumer groups, rebalancing, competing consumers
- [ ] **Operations:** slow consumers, lag management, replay, retention, and schema registries
- [ ] **Transactions:** outbox/inbox patterns and transactional messaging
- [ ] **Error handling:** poison pills, circuit-breaking consumers, dead-letter topics (DLT)

### 7. Idempotency & Retries
- [ ] Designing idempotent API endpoints, unique idempotency keys
- [ ] Handling retry storms, deduplication layers

### 8. Distributed Caching & High-Concurrency Failures
- [ ] Cache stampede (thundering herd)
- [ ] Hot-key / big-key mitigation
- [ ] Cache penetration, cache avalanche, Bloom filters

### 9. Rate Limiting & Throttling
- [ ] **Algorithms:** fixed window, sliding window log, token bucket, leaky bucket
- [ ] **Scopes:** per-user vs per-IP vs per-API
- [ ] **Architecture:** distributed rate limiting (Redis token bucket, in-memory instances, gateway throttling)
- [ ] **Trade-offs:** accuracy (strict sync) vs performance/latency

### 10. Backpressure, Admission Control & Overload Protection
- [ ] Producer/consumer backpressure and bounded queues
- [ ] Load shedding, admission control, and concurrency limits
- [ ] Queue lag, saturation, and adaptive throttling
- [ ] Retry budgets and preventing retry amplification
- [ ] Tail latency and coordinated omission

### 11. Fault Tolerance, Resilience & Failure Handling
- [ ] **Strategies:** fail-fast vs graceful degradation, timeouts, retries with exponential backoff + jitter
- [ ] **Patterns:** circuit breakers, bulkheads, isolating partial failures, cascading failure prevention

### 12. Data Consistency & Clock Synchronization
- [ ] **CAP theorem:** consistency vs availability vs partition tolerance
- [ ] **PACELC theorem:** normal (latency vs consistency) vs partition state
- [ ] **Consistency models:** strong, eventual, read-your-writes, monotonic reads
- [ ] **Distributed clocks:** vector clocks, Lamport timestamps, TrueTime

### 13. Storage Types - Latency, Cost & Trade-offs
- [ ] **Physical:** NVMe SSDs vs HDDs, sequential vs random access
- [ ] **File-based:** network file systems, object storage (S3), distributed FS (HDFS)
- [ ] **Database:** block storage volumes, log-structured storage engines
- [ ] **Log/sequential:** append-only transaction logs, write-ahead logs (WAL)

### 14. Observability, Monitoring & Alerting
- [ ] **Pillars:** metrics vs logs vs traces
- [ ] **Frameworks:** RED (Rate, Errors, Duration), USE (Utilization, Saturation, Errors), 4 Golden Signals
- [ ] **Governance:** SLIs, SLOs, SLAs
- [ ] **Logistics:** distributed tracing (span propagation, trace contexts), alert fatigue, thresholds, OpenTelemetry, Jaeger, Prometheus, ELK

### 15. Single Region vs Multi-Region Deployment
- [ ] **Topologies:** single region active-only, active-passive, active-active
- [ ] **Metrics:** RPO vs RTO under different faults, split-brain handling, global traffic management

### 16. Data Migration & Zero-Downtime Evolution
- [ ] Expand-and-contract schema migrations and version skew
- [ ] Dual reads, dual writes, backfills, and validation
- [ ] Shadow traffic and CDC-based migrations
- [ ] Repartitioning and re-sharding live systems
- [ ] Rollback and reconciliation strategies

### 17. Disaster Recovery & Operational Readiness
- [ ] Backup strategies and regular restore testing
- [ ] Regional evacuation and dependency failure planning
- [ ] RPO/RTO-driven architecture and disaster recovery runbooks
- [ ] Game days, chaos engineering, and capacity headroom
- [ ] Incident response and blameless postmortems

### 18. Batch, Stream & Workflow Processing
- [ ] Batch vs stream processing
- [ ] Event time vs processing time; windows and watermarks
- [ ] Late and out-of-order events
- [ ] Stateful stream processing, checkpoints, and recovery
- [ ] Workflow orchestration; scheduled and long-running jobs
- [ ] Exactly-once claims and their practical boundaries

### 19. Multi-Tenancy, Isolation & Fairness
- [ ] Shared vs isolated tenant models
- [ ] Tenant-aware partitioning and data isolation
- [ ] Noisy-neighbor and hot-tenant mitigation
- [ ] Per-tenant quotas, rate limits, and fair resource allocation
- [ ] Cost attribution

### 20. Security, Privacy & Abuse Resistance
- [ ] Threat modeling and trust boundaries
- [ ] Least privilege and service-to-service identity
- [ ] Encryption, key management, and key rotation
- [ ] PII handling, retention, and audit trails
- [ ] Replay protection and request signing
- [ ] DDoS and abuse prevention

## How to Use These Notes
- Read a topic, then try to **draw the system** or **code the design** from memory.
- For any decision ask: *what does this optimize for, and what does it cost?*
- Tie theory back to the **`pocs/`** folder—build small versions to feel it.
- Check items off as you master them.
- Split a large topic into its own `.md` file only when the extra detail is useful.
