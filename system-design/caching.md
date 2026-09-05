# Caching

## Why cache
Reduce latency, offload backends, and increase throughput by keeping hot data
closer/faster.

## Where caching happens
- **Client** (browser)
- **CDN / edge**
- **Application** (in-process, e.g. Caffeine)
- **Distributed cache** (Redis, Memcached)
- **Database** (query/result cache, buffer pool)

## Caching patterns
- **Cache-aside (lazy loading)** — app checks cache, loads DB on miss, populates cache. Most common.
- **Read-through** — cache library loads from DB on miss.
- **Write-through** — write to cache and DB synchronously (consistent, slower writes).
- **Write-behind (write-back)** — write to cache, async flush to DB (fast, risk of loss).

## Eviction policies
LRU, LFU, FIFO, and TTL-based expiry. Pick based on access patterns.

## The hard problems
- **Invalidation** — "there are only two hard things..." Keep cache and source of truth in sync.
- **Stampede / thundering herd** — many misses at once; mitigate with locks, request coalescing, jittered TTLs.
- **Hot keys** — a single key overwhelms a node; shard or replicate it.
- **Cold start** — warm caches proactively for critical data.

## Consistency
Caches trade freshness for speed. Decide acceptable staleness per use case.

## Trade-offs
- **Speed & load reduction** vs **staleness + invalidation complexity**.
- **Write-through** consistency vs **write-back** performance (and durability risk).
- **In-process** cache is fastest but not shared; **distributed** cache is shared but adds a network hop.
