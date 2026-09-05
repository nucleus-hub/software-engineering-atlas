# System Design

A structured curriculum for learning system design and low-level design (LLD),
split into two tiers. Work through **Basics** first, then **Advanced**.

## Structure

```
system-design/
├── basics/      # foundations: LLD, APIs, caching, DBs, partitioning, async, threads
└── advanced/    # deep dives: consensus, event-driven, resilience, consistency, multi-region
```

## Curriculum at a Glance

### [Basics](basics/README.md)
1. LLD: Object-Oriented Principles & Clean Code
2. LLD: Creational & Structural Design Patterns
3. API Design & Service Communication
4. Load Balancing & Proxying
5. Caching Core
6. Database Fundamentals & Internal Architecture
7. Data Partitioning, Sharding & Replication
8. Asynchronous Processing Basics
9. Threads, Thread Pools, Parallelization

### [Advanced](advanced/README.md)
1. LLD: Behavioral Design Patterns
2. LLD: Real-World Machine Coding Case Studies
3. Concurrency Control, Race Conditions & Locking
4. Distributed Transactions & Consensus
5. Event-Driven Systems & Message Queues
6. Idempotency & Retries
7. Distributed Caching & High-Concurrency Failures
8. Rate Limiting & Throttling
9. Fault Tolerance, Resilience & Failure Handling
10. Data Consistency & Clock Synchronization
11. Storage Types - Latency, Cost & Trade-offs
12. Observability, Monitoring & Alerting
13. Single Region vs Multi-Region Deployment

## How to use these notes
- Read a topic, then try to **draw the system** or **code the design** from memory.
- For any decision ask: *what does this optimize for, and what does it cost?*
- Tie theory back to the **`pocs/`** folder - build small versions to feel it.
- Check items off as you master them.
