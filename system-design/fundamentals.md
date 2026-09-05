# System Design Fundamentals

## What "system design" optimizes
Balancing **functional requirements** (what it does) with **non-functional
requirements**: scalability, availability, latency, consistency, durability,
cost, security, and maintainability.

## Core building blocks
- **Client / Server** and the request lifecycle
- **DNS** and how names resolve to addresses
- **Load balancers** (L4 vs L7)
- **Application servers** (stateless where possible)
- **Databases** (SQL / NoSQL)
- **Caches** (in-memory, distributed)
- **CDNs** for static/edge content
- **Message queues** for async decoupling
- **Object storage** for blobs

## Key concepts
- **Latency vs throughput** — response time vs work per unit time.
- **Availability** — measured in "nines" (99.9% = ~8.76h downtime/yr).
- **Reliability & durability** — will it work correctly; will data survive.
- **Consistency models** — strong, eventual, causal.
- **Back-of-the-envelope estimation** — QPS, storage, bandwidth.

## A repeatable design method
1. **Clarify requirements** (functional + non-functional, scale).
2. **Estimate** (traffic, storage, bandwidth).
3. **Define APIs** (contracts first).
4. **High-level design** (boxes and arrows).
5. **Deep dive** (data model, hot paths, bottlenecks).
6. **Address failure** (redundancy, retries, timeouts).
7. **Evaluate trade-offs**.

## Back-of-the-envelope numbers worth memorizing
- L1 cache ref: ~1 ns; main memory ref: ~100 ns
- SSD random read: ~100 us; disk seek: ~10 ms
- Same-datacenter round trip: ~0.5 ms; cross-continent: ~150 ms
- 1 day ~= 86,400 s (~100k) -> handy for QPS math

## Trade-offs
- **Simplicity vs flexibility** — over-engineering is a cost; YAGNI applies.
- **Consistency vs availability** — see CAP in distributed-systems.
- **Latency vs cost** — more replicas/edge = faster but pricier.
- **Build vs buy** — managed services trade control for speed.
