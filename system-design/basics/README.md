# System Design - Basics

Foundational system design and low-level design (LLD) topics. Start here before
moving on to [`../advanced`](../advanced/README.md). Check items off as you learn them.

---

## 1. LLD: Object-Oriented Principles & Clean Code
- [ ] **SOLID principles** (simple explanations + examples):
  - Single Responsibility
  - Open/Closed
  - Liskov Substitution
  - Interface Segregation
  - Dependency Inversion
- [ ] **Clean code fundamentals:** DRY, KISS, YAGNI
- [ ] Encapsulation, polymorphism, composition vs inheritance

## 2. LLD: Creational & Structural Design Patterns
- [ ] **Creational:** Singleton, Factory Method, Abstract Factory, Builder, Prototype
- [ ] **Structural:** Adapter, Decorator, Facade, Proxy

## 3. API Design & Service Communication
- [ ] **Protocols & paradigms:** REST vs gRPC vs GraphQL
- [ ] WebSockets, long polling, Server-Sent Events (SSE)
- [ ] **Lifecycle:** synchronous vs asynchronous communication
- [ ] Versioning strategies, backward compatibility, schema evolution

## 4. Load Balancing & Proxying
- [ ] **Types:** Layer 4 (transport), Layer 7 (application), DNS-based
- [ ] **Infrastructure:** proxies, reverse proxies, Anycast routing, Envoy, Nginx
- [ ] **Strategies:** round-robin, least connections, IP hash, weighted

## 5. Caching Core
- [ ] **Types:** client-side (browser), CDN, reverse proxy, application, distributed
- [ ] **Strategies:** write-through, write-around, write-back, cache-aside
- [ ] **Eviction policies:** LRU, LFU, FIFO, TTL-based

## 6. Database Fundamentals & Internal Architecture
- [ ] **ACID:** Atomicity, Consistency, Isolation, Durability
- [ ] **SQL vs NoSQL:** high-level trade-offs, when to choose which
- [ ] **NoSQL types:** key-value (Redis), document (MongoDB), wide-column (Cassandra), graph (Neo4j)
- [ ] **Storage & indexing:** B-Trees vs LSM-Trees, indexing trade-offs, read/write amplification
- [ ] **Schema design:** normalization (1NF, 2NF, 3NF) vs de-normalization

## 7. Data Partitioning, Sharding & Replication
- [ ] Horizontal vs vertical scaling, range-based partitioning, consistent hashing
- [ ] **Sharding execution:** SQL manual sharding (app-level routing, re-sharding) vs NoSQL native partitioning (hash keys)
- [ ] **Replication topologies:** master-slave, multi-master, peer-to-peer

## 8. Asynchronous Processing Basics
- [ ] Message queues, pub/sub mechanics
- [ ] Dead-letter queues (DLQ), message durability
- [ ] RabbitMQ, ActiveMQ

## 9. Threads, Thread Pools, Parallelization
- [ ] **Java/Spring Boot:** thread pool config (TaskExecutor, Tomcat thread pools)
- [ ] **Optimization:** tuning core/max pool sizes, queue capacity limits, rejection policies

---

> Split any topic into its own `.md` file here as your notes grow (e.g. `solid.md`).
