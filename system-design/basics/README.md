# System Design - Basics

Foundational system design and low-level design (LLD) topics. Start here before
moving on to [`../advanced`](../advanced/README.md). Check items off as you learn them.

---

## 1. System Design Interview Framework & Capacity Estimation
- [ ] Functional vs non-functional requirements
- [ ] Constraints, assumptions, scope control, and identifying core use cases
- [ ] Read/write QPS, peak traffic, storage, bandwidth, and memory estimation
- [ ] Latency, availability, durability, and consistency targets
- [ ] High-level design, bottleneck analysis, and selecting deep dives
- [ ] Back-of-the-envelope calculations and validating estimates

## 2. LLD: Object-Oriented Principles & Clean Code
- [ ] **SOLID principles** (simple explanations + examples):
  - Single Responsibility
  - Open/Closed
  - Liskov Substitution
  - Interface Segregation
  - Dependency Inversion
- [ ] **Clean code fundamentals:** DRY, KISS, YAGNI
- [ ] Encapsulation, polymorphism, composition vs inheritance

## 3. LLD: Creational & Structural Design Patterns
- [ ] **Creational:** Singleton, Factory Method, Abstract Factory, Builder, Prototype
- [ ] **Structural:** Adapter, Decorator, Facade, Proxy

## 4. Networking & Request Lifecycle
- [ ] DNS resolution, caching, and common failure modes
- [ ] TCP vs UDP; TLS termination and HTTPS
- [ ] HTTP/1.1 vs HTTP/2 vs HTTP/3
- [ ] Connection pooling, keep-alive, and timeout budgets
- [ ] Request path: client → DNS/CDN → load balancer → service → database
- [ ] Latency sources and network failure modes

## 5. Architecture Styles & Service Decomposition
- [ ] Layered architecture and modular monoliths vs microservices
- [ ] Stateless vs stateful services
- [ ] Service boundaries, ownership, and bounded contexts
- [ ] Shared database vs database per service
- [ ] Service discovery and configuration management

## 6. API Correctness, Security & Resource Design
- [ ] Resource-oriented API design; pagination, filtering, sorting, and partial updates
- [ ] Authentication vs authorization; sessions, cookies, OAuth 2.0, OIDC, and JWT trade-offs
- [ ] Request validation, standardized errors, timeouts, and request-size limits
- [ ] Secrets handling and encryption in transit and at rest

## 7. API Design & Service Communication
- [ ] **Protocols & paradigms:** REST vs gRPC vs GraphQL
- [ ] WebSockets, long polling, Server-Sent Events (SSE)
- [ ] **Lifecycle:** synchronous vs asynchronous communication
- [ ] Versioning strategies, backward compatibility, schema evolution

## 8. Load Balancing & Proxying
- [ ] **Types:** Layer 4 (transport), Layer 7 (application), DNS-based
- [ ] **Infrastructure:** proxies, reverse proxies, Anycast routing, Envoy, Nginx
- [ ] **Strategies:** round-robin, least connections, IP hash, weighted

## 9. Caching Core
- [ ] **Types:** client-side (browser), CDN, reverse proxy, application, distributed
- [ ] **Strategies:** write-through, write-around, write-back, cache-aside
- [ ] **Eviction policies:** LRU, LFU, FIFO, TTL-based

## 10. Database Fundamentals & Internal Architecture
- [ ] **ACID:** Atomicity, Consistency, Isolation, Durability
- [ ] **SQL vs NoSQL:** high-level trade-offs, when to choose which
- [ ] **NoSQL types:** key-value (Redis), document (MongoDB), wide-column (Cassandra), graph (Neo4j)
- [ ] **Storage & indexing:** B-Trees vs LSM-Trees, indexing trade-offs, read/write amplification
- [ ] **Schema design:** normalization (1NF, 2NF, 3NF) vs de-normalization

## 11. Practical Data Modeling & Query Design
- [ ] Model schemas from access patterns
- [ ] Primary, composite, secondary, and covering indexes
- [ ] Query plans, index selectivity, and avoiding unbounded scans
- [ ] One-to-many and many-to-many relationships
- [ ] Offset vs cursor/keyset pagination
- [ ] Partition-key and sort-key selection; avoiding N+1 queries

## 12. Data Partitioning, Sharding & Replication
- [ ] Horizontal vs vertical scaling, range-based partitioning, consistent hashing
- [ ] **Sharding execution:** SQL manual sharding (app-level routing, re-sharding) vs NoSQL native partitioning (hash keys)
- [ ] **Replication topologies:** master-slave, multi-master, peer-to-peer

## 13. Asynchronous Processing Basics
- [ ] Message queues, pub/sub mechanics
- [ ] Dead-letter queues (DLQ), message durability
- [ ] RabbitMQ, ActiveMQ

## 14. Availability & Deployment Fundamentals
- [ ] Health, liveness, and readiness checks
- [ ] Redundancy, failure domains, and removing single points of failure
- [ ] Stateless horizontal scaling and basic availability calculations
- [ ] Rolling, blue-green, and canary deployments
- [ ] Graceful shutdown and connection draining
- [ ] Backups and basic restore procedures

## 15. Distributed ID Generation
- [ ] Database sequences and allocation strategies
- [ ] UUID versions and their trade-offs
- [ ] ULID and other time-sortable identifiers
- [ ] Snowflake-style IDs
- [ ] Collision, ordering, predictability, and index-locality concerns

## 16. Threads, Thread Pools, Parallelization
- [ ] CPU-bound vs I/O-bound work and concurrency vs parallelism
- [ ] Little's Law, bounded queues, and thread-pool exhaustion
- [ ] **Java/Spring Boot:** thread pool config (TaskExecutor, Tomcat thread pools)
- [ ] **Optimization:** tuning core/max pool sizes, queue capacity limits, rejection policies

---

> Split any topic into its own `.md` file here as your notes grow (e.g. `solid.md`).
