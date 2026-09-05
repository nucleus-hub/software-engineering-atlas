# Scalability

## Vertical vs horizontal
- **Vertical (scale up)** — bigger machine. Simple, but a ceiling and a single failure domain.
- **Horizontal (scale out)** — more machines. Near-limitless, but needs statelessness + coordination.

## Statelessness
Keep application servers **stateless** so any node can serve any request.
Push state to databases, caches, or the client (tokens). This unlocks easy
horizontal scaling and rolling deploys.

## Load balancing
- **L4** (transport) vs **L7** (application-aware routing).
- Algorithms: round-robin, least-connections, IP-hash, weighted.
- Health checks + graceful draining.

## Scaling reads
- **Read replicas**, **caching**, **CDNs**, denormalized read models (CQRS).

## Scaling writes
- **Sharding/partitioning**, **write batching**, **async processing** via queues.
- Beware hotspots; choose partition keys carefully.

## Asynchronous processing
Move slow/non-critical work off the request path with **queues** and
**workers** (email, thumbnails, analytics). Improves perceived latency and
smooths spikes (load leveling).

## Autoscaling
- Reactive (metrics-based: CPU, QPS, queue depth) vs scheduled (known patterns).
- Watch for **thundering herd** and cold starts.

## Bottleneck hunting
Measure first. Common culprits: the database, N+1 queries, lock contention,
chatty network calls, GC pauses, and unbounded thread pools.

## Trade-offs
- **Scale out** adds coordination + operational complexity vs simple scale up.
- **Caching** boosts read scale but adds staleness + invalidation complexity.
- **Async** improves responsiveness but complicates error handling and observability.
- **Sharding** unlocks write scale but makes cross-shard queries/transactions hard.
