# Trade-offs Cheat Sheet

System design has no free lunch. Quick reference for the classic tensions.

| Decision | You gain | You pay |
|----------|----------|---------|
| Vertical vs horizontal scaling | Simplicity vs near-limitless scale | Ceiling/SPOF vs coordination complexity |
| SQL vs NoSQL | Integrity + rich queries vs flexibility + scale | Rigid schema/scale limits vs weaker guarantees |
| Normalization vs denormalization | Clean writes vs fast reads | More joins vs update anomalies |
| Strong vs eventual consistency | Correctness vs availability/latency | Higher latency/less availability vs staleness |
| Sync vs async communication | Simplicity/immediacy vs decoupling/resilience | Temporal coupling vs eventual consistency + ops |
| Monolith vs microservices | Simplicity vs autonomy/independent scale | Big ball of mud vs distributed complexity |
| Caching | Speed + load reduction | Staleness + invalidation |
| More replicas | Durability + read scale | Write cost + staleness window |
| More indexes | Faster reads | Slower writes + storage |
| Build vs buy | Control vs speed | Maintenance burden vs vendor lock-in/cost |
| Write-through vs write-back cache | Consistency vs write speed | Slower writes vs data-loss risk |

## Mental models
- **CAP / PACELC** — consistency vs availability vs latency under/without partitions.
- **Amdahl's Law** — speedup is limited by the serial portion.
- **Little's Law** — L = lambda x W (concurrency = arrival rate x latency).
- **The Eight Fallacies** of distributed computing.
- **YAGNI / KISS / DRY** — resist speculative complexity.
- **Conway's Law** — system structure mirrors org structure.

## The one question
For any choice: **"What does this optimize for, and what does it cost?"**
If you can't name the cost, you haven't understood the decision yet.
