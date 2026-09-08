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
1. System Design Interview Framework & Capacity Estimation
2. LLD: Object-Oriented Principles & Clean Code
3. LLD: Creational & Structural Design Patterns
4. Networking & Request Lifecycle
5. Architecture Styles & Service Decomposition
6. API Correctness, Security & Resource Design
7. API Design & Service Communication
8. Load Balancing & Proxying
9. Caching Core
10. Database Fundamentals & Internal Architecture
11. Practical Data Modeling & Query Design
12. Data Partitioning, Sharding & Replication
13. Asynchronous Processing Basics
14. Availability & Deployment Fundamentals
15. Distributed ID Generation
16. Threads, Thread Pools, Parallelization

### [Advanced](advanced/README.md)
1. LLD: Behavioral Design Patterns
2. LLD: Real-World Machine Coding Case Studies
3. Concurrency Control, Race Conditions & Locking
4. Distributed Transactions & Consensus
5. Advanced Replication, Quorums & Conflict Resolution
6. Event-Driven Systems & Message Queues
7. Idempotency & Retries
8. Distributed Caching & High-Concurrency Failures
9. Rate Limiting & Throttling
10. Backpressure, Admission Control & Overload Protection
11. Fault Tolerance, Resilience & Failure Handling
12. Data Consistency & Clock Synchronization
13. Storage Types - Latency, Cost & Trade-offs
14. Observability, Monitoring & Alerting
15. Single Region vs Multi-Region Deployment
16. Data Migration & Zero-Downtime Evolution
17. Disaster Recovery & Operational Readiness
18. Batch, Stream & Workflow Processing
19. Multi-Tenancy, Isolation & Fairness
20. Security, Privacy & Abuse Resistance

## How to use these notes
- Read a topic, then try to **draw the system** or **code the design** from memory.
- For any decision ask: *what does this optimize for, and what does it cost?*
- Tie theory back to the **`pocs/`** folder - build small versions to feel it.
- Check items off as you master them.
