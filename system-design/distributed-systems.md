# Distributed Systems

## Why distribute
Single machines hit limits (CPU, memory, disk, failure domain). Distributing
buys **scale** and **fault tolerance** at the cost of **complexity**.

## Fallacies of distributed computing (memorize these)
The network is *not* reliable, latency is *not* zero, bandwidth is *not*
infinite, the network is *not* secure, topology *changes*, there is *no*
single admin, transport cost is *not* zero, the network is *not* homogeneous.

## CAP theorem
Under a network **P**artition you must choose between **C**onsistency and
**A**vailability.
- **CP** systems reject/So block on partition to stay consistent (e.g. many RDBMS, ZooKeeper).
- **AP** systems stay available but may serve stale data (e.g. Dynamo-style stores).
- Note: PACELC extends this — Else (no partition), choose Latency vs Consistency.

## Consistency models
- **Strong / linearizable** — reads see the latest write.
- **Sequential / causal** — ordering guarantees, weaker than linearizable.
- **Eventual** — replicas converge given no new writes.

## Replication
- **Leader-follower (primary-replica)** — writes to leader, reads can fan out.
- **Multi-leader** — write anywhere, needs conflict resolution.
- **Leaderless (quorum)** — R + W > N for overlap.

## Partitioning (sharding)
- By **hash** (even spread, poor range queries)
- By **range** (great range queries, risk of hotspots)
- **Consistent hashing** to minimize reshuffle on node changes

## Consensus
- **Raft** / **Paxos** for agreeing on a value/log across nodes.
- Used for leader election, config, distributed locks.

## Time and ordering
- Physical clocks drift -> use **logical clocks** (Lamport) and **vector clocks**.

## Failure handling
- **Timeouts**, **retries with backoff + jitter**, **idempotency keys**
- **Circuit breakers**, **bulkheads**, **health checks**
- **Idempotency** is the antidote to at-least-once delivery.

## Trade-offs
- **Consistency vs availability vs latency** (CAP/PACELC).
- **More replicas** improve durability/reads but increase write cost & staleness windows.
- **Coordination** (consensus) adds latency; avoid on the hot path when possible.
