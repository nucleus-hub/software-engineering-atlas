# System Design

Deep-dive notes on designing large, reliable, scalable systems. This is a
**living document** — refine it as your understanding grows. System design is
the art of choosing which problems to have, so every section ends with
**trade-offs**.

> Kept as a single README for now. When a topic outgrows its section, split it
> into its own `.md` file (e.g. `databases.md`) and link it from the index below.

## Index
1. [Fundamentals](#1-fundamentals)
2. [Distributed Systems](#2-distributed-systems)
3. [Scalability](#3-scalability)
4. [Databases](#4-databases)
5. [Caching](#5-caching)
6. [Messaging](#6-messaging)
7. [Microservices](#7-microservices)
8. [Architecture Patterns](#8-architecture-patterns)
9. [Case Studies](#9-case-studies)
10. [Trade-offs Cheat Sheet](#10-trade-offs-cheat-sheet)

### How to use these notes
- Read a topic, then try to **draw the system** from memory.
- For any decision ask: *what does this optimize for, and what does it cost?*
- Tie theory back to the **`pocs/`** folder — build small versions to feel it.

---

## 1. Fundamentals

**What system design optimizes:** balancing functional requirements (what it
does) with non-functional ones: scalability, availability, latency,
consistency, durability, cost, security, maintainability.

**Building blocks:** client/server, DNS, load balancers (L4 vs L7), stateless
app servers, databases (SQL/NoSQL), caches, CDNs, message queues, object storage.

**Key concepts:** latency vs throughput; availability in "nines"
(99.9% = ~8.76h downtime/yr); reliability & durability; consistency models
(strong/eventual/causal); back-of-the-envelope estimation.

**A repeatable method:**
1. Clarify requirements (functional + non-functional + scale)
2. Estimate (traffic, storage, bandwidth)
3. Define APIs (contracts first)
4. High-level design (boxes and arrows)
5. Deep dive (data model, hot paths, bottlenecks)
6. Address failure (redundancy, retries, timeouts)
7. Evaluate trade-offs

**Numbers worth memorizing:** L1 ref ~1 ns; memory ref ~100 ns; SSD random read
~100 us; disk seek ~10 ms; same-DC round trip ~0.5 ms; cross-continent ~150 ms;
1 day ~= 86,400 s (~100k) for QPS math.

**Trade-offs:** simplicity vs flexibility (YAGNI); consistency vs availability;
latency vs cost; build vs buy.

---

## 2. Distributed Systems

**Why distribute:** single machines hit CPU/memory/disk/failure-domain limits.
Distributing buys scale and fault tolerance at the cost of complexity.

**The eight fallacies:** the network is *not* reliable; latency is *not* zero;
bandwidth is *not* infinite; the network is *not* secure; topology *changes*;
there is *no* single admin; transport cost is *not* zero; the network is *not*
homogeneous.

**CAP / PACELC:** under a **P**artition, choose **C**onsistency or
**A**vailability. PACELC adds: **E**lse (no partition) choose **L**atency vs
**C**onsistency.

**Consistency models:** strong/linearizable -> sequential/causal -> eventual.

**Replication:** leader-follower, multi-leader (conflict resolution),
leaderless quorum (R + W > N).

**Partitioning (sharding):** by hash (even spread, poor ranges), by range
(good ranges, hotspot risk), consistent hashing (minimal reshuffle).

**Consensus:** Raft/Paxos for leader election, config, distributed locks.

**Time & ordering:** clocks drift; use logical (Lamport) and vector clocks.

**Failure handling:** timeouts, retries with backoff + jitter, idempotency
keys, circuit breakers, bulkheads, health checks.

**Trade-offs:** consistency vs availability vs latency; more replicas improve
durability/reads but raise write cost and staleness; coordination adds latency.

---

## 3. Scalability

**Vertical (scale up)** — bigger box; simple but a ceiling + single failure
domain. **Horizontal (scale out)** — more boxes; near-limitless but needs
statelessness + coordination.

**Statelessness:** keep app servers stateless (state in DB/cache/token) to
unlock horizontal scaling and rolling deploys.

**Load balancing:** L4 vs L7; round-robin/least-connections/IP-hash/weighted;
health checks + graceful draining.

**Scale reads:** read replicas, caching, CDNs, denormalized read models (CQRS).
**Scale writes:** sharding, batching, async via queues; avoid hot partition keys.

**Async processing:** move slow/non-critical work off the request path with
queues + workers (load leveling).

**Autoscaling:** reactive (CPU/QPS/queue depth) vs scheduled; beware thundering
herd + cold starts.

**Bottleneck hunting:** measure first. Usual suspects: the DB, N+1 queries,
lock contention, chatty calls, GC pauses, unbounded thread pools.

**Trade-offs:** scale-out coordination cost vs scale-up simplicity; caching
speed vs staleness; async responsiveness vs error-handling complexity;
sharding write-scale vs hard cross-shard queries.

---

## 4. Databases

**SQL vs NoSQL:** relational = strong schema, ACID, joins, integrity. NoSQL
families: document (Mongo), key-value (Redis/Dynamo), wide-column (Cassandra),
graph (Neo4j).

**ACID vs BASE:** Atomicity/Consistency/Isolation/Durability vs Basically
Available, Soft state, Eventual consistency.

**Isolation levels:** Read Uncommitted -> Read Committed -> Repeatable Read ->
Serializable. Anomalies: dirty read, non-repeatable read, phantom read.

**Indexing:** B-tree (range+equality), hash (equality), composite, covering.
Indexes speed reads, slow writes, cost space — index for real query patterns.

**Normalization vs denormalization:** normalize to reduce redundancy/anomalies;
denormalize for read speed, accepting update complexity.

**Scaling:** replication (read/HA), partitioning/sharding (writes), connection
pooling, read/write splitting, CQRS. **Migrations:** Flyway/Liquibase, prefer
backward-compatible expand/contract.

**Trade-offs:** SQL integrity+querying vs NoSQL flexibility+scale;
normalization vs denormalization; strong isolation vs throughput; more indexes
= faster reads / slower writes.

---

## 5. Caching

**Why:** reduce latency, offload backends, raise throughput.

**Where:** client, CDN/edge, in-process (Caffeine), distributed
(Redis/Memcached), database.

**Patterns:** cache-aside (lazy, most common), read-through, write-through
(consistent, slower writes), write-behind (fast, risk of loss).

**Eviction:** LRU, LFU, FIFO, TTL.

**Hard problems:** invalidation; stampede/thundering herd (locks, request
coalescing, jittered TTLs); hot keys (shard/replicate); cold start (warm
proactively).

**Trade-offs:** speed + load reduction vs staleness + invalidation complexity;
write-through consistency vs write-back performance; in-process speed vs
distributed sharing.

---

## 6. Messaging

**Why async:** decouple producers/consumers, absorb spikes (load leveling),
enable event-driven architectures, improve resilience.

**Queues vs logs vs pub/sub:** queue (RabbitMQ/SQS, consumed once); log
(Kafka, append-only, replayable, multi-consumer offsets); pub/sub (fan-out).

**Delivery semantics:** at-most-once (may lose), at-least-once (may duplicate
-> consumers must be idempotent), exactly-once (hardest, "effectively once").

**Ordering:** global ordering is costly; Kafka orders within a partition — use
a partition key for related events.

**Concerns:** backpressure, dead-letter queues, consumer groups, schema
evolution (registry + compatible changes).

**Patterns:** event-driven, event sourcing, CQRS, outbox, saga.

**Trade-offs:** decoupling/resilience vs infra + eventual consistency +
debugging; at-least-once simplicity vs idempotency burden; strong ordering vs
throughput; queue simplicity vs log replayability.

---

## 7. Microservices

**Monolith vs microservices:** monolith = one deployable, simple early, risks a
big ball of mud. Microservices = independently deployable services around
business capabilities; autonomy + independent scaling vs distributed
complexity. **Start with a modular monolith**; extract when boundaries + pain
are clear.

**Decomposition:** around bounded contexts (DDD), not technical layers; each
service owns its data (no shared DB).

**Communication:** sync (REST/gRPC, temporal coupling) vs async (events, looser
coupling, eventual consistency).

**Cross-cutting:** API gateway, service discovery, centralized config,
resilience (timeouts/retries/circuit breakers/bulkheads), observability
(logs/metrics/tracing + correlation IDs).

**Data:** database per service, saga (choreography vs orchestration), outbox,
CQRS.

**Trade-offs:** autonomy + independent scaling vs operational + distributed
complexity; independent deploys vs harder end-to-end testing; polyglot freedom
vs consistency cost. Remember Conway's Law.

---

## 8. Architecture Patterns

**Application:** layered (n-tier), hexagonal (ports & adapters), clean/onion,
modular monolith.

**Domain modeling:** DDD — bounded contexts, aggregates, ubiquitous language.

**Data & flow:** CQRS, event sourcing, event-driven architecture, saga, outbox.

**Integration:** API gateway, backend-for-frontend (BFF), strangler fig,
sidecar, anti-corruption layer.

**Deployment:** blue-green, canary, rolling; feature flags (decouple deploy
from release).

**Reliability:** circuit breaker, retry w/ backoff, bulkhead, rate limiting,
timeout, fallback/graceful degradation.

**Trade-offs:** layered simplicity vs hexagonal/clean testability+indirection;
event sourcing auditability vs complexity; CQRS scaling vs two models. Apply
patterns where pain justifies them — avoid cargo-culting.

---

## 9. Case Studies

Work through end-to-end designs; follow the method in
[Fundamentals](#1-fundamentals) and always close with trade-offs.

**Suggested:** URL shortener, pastebin, rate limiter, news feed, chat system,
notification system, web crawler, search autocomplete, video streaming,
ride-sharing, payment system, distributed KV store, distributed job scheduler.

**Template per case study:** requirements -> scale estimates -> API design ->
high-level architecture -> data model/storage -> deep dives -> bottlenecks &
scaling -> failure handling -> trade-offs.

---

## 10. Trade-offs Cheat Sheet

| Decision | You gain | You pay |
|----------|----------|---------|
| Vertical vs horizontal scaling | Simplicity vs limitless scale | Ceiling/SPOF vs coordination |
| SQL vs NoSQL | Integrity + queries vs flexibility + scale | Rigid schema vs weaker guarantees |
| Normalize vs denormalize | Clean writes vs fast reads | More joins vs update anomalies |
| Strong vs eventual consistency | Correctness vs availability/latency | Latency vs staleness |
| Sync vs async communication | Immediacy vs decoupling | Temporal coupling vs eventual consistency |
| Monolith vs microservices | Simplicity vs autonomy | Big ball of mud vs distributed complexity |
| Caching | Speed + load reduction | Staleness + invalidation |
| More replicas | Durability + read scale | Write cost + staleness |
| More indexes | Faster reads | Slower writes + storage |
| Build vs buy | Control vs speed | Maintenance vs lock-in/cost |
| Write-through vs write-back | Consistency vs write speed | Slower writes vs data-loss risk |

**Mental models:** CAP/PACELC; Amdahl's Law (serial portion limits speedup);
Little's Law (L = lambda x W); the eight fallacies; YAGNI/KISS/DRY; Conway's Law.

**The one question:** *"What does this optimize for, and what does it cost?"*
If you can't name the cost, you haven't understood the decision yet.
