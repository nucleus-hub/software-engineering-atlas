# System Design Interview Framework & Capacity Estimation

> A compact, visual guide for turning an ambiguous prompt into a defensible design. Use it to structure the interview, quantify scale, expose risks, and explain why each decision is appropriate.

---

## 1. One-page visual summary

![Six-stage system design interview framework](assets/topic-01/interview_framework.png)

The framework is a narrowing funnel: establish what matters, quantify it, define contracts, draw critical paths, stress the risky parts, and defend the resulting trade-offs.

![Proportional 45-minute system design interview timeline](assets/topic-01/interview_timeline.png)

| Phase | Time | Deliverable |
|---|---:|---|
| Clarify | 0–5 min | Core use cases, constraints, out-of-scope items |
| Quantify | 5–10 min | Peak QPS, read/write ratio, storage, SLOs |
| Contract | 10–15 min | Minimal APIs/events and core entities |
| Design | 15–25 min | Read, write, and asynchronous paths |
| Stress | 25–38 min | Deep dives into the largest risks |
| Fail | 38–43 min | Degraded behavior and recovery |
| Close | 43–45 min | Decisions, trade-offs, and evolution trigger |

!!! tip "The interview in one sentence"
    Given the requirements and scale, choose the simplest architecture that works; explain its failure behavior, cost, and trigger for evolution.

---

## 2. Core mental model

### Requirements → load → paths → pressure → decision

1. **Requirements** define what success means.
2. **Load estimates** reveal which resources may become constrained.
3. **Critical paths** show where latency and availability are spent.
4. **Pressure tests** expose bottlenecks and failure propagation.
5. **Decisions** balance product priorities rather than chasing universal “best practices.”

![Synchronous critical path and decoupled asynchronous work](assets/topic-01/critical_path.png)

The synchronous path determines user latency and immediate availability. Optional analytics, notifications, and fan-out work should leave that path when delayed completion is acceptable.

### Capacity is derived—not guessed

Start with users and operations, not formulas. Each quantity below only matters because it feeds a decision, so walk through one small running example first: a photo-sharing feed with **10 million daily active users**, each opening the feed **5 times a day**, where each feed response is about **20 KB**.

**QPS (queries per second)** is just how many requests land on the system every second. It is rarely stated directly — you derive it from daily active users and how often they act:

```text
Average QPS = operations per day / 86,400   (seconds in a day)
            = (10,000,000 users × 5 opens) / 86,400
            ≈ 578 requests/second
```

Traffic is never flat — lunchtime, a push notification, or a viral post can spike load well above the daily average. A **peak factor** captures that spike as a multiplier on the average:

```text
Peak QPS = average QPS × peak factor
         = 578 × 3 (assume 3× at busiest hour)
         ≈ 1,734 requests/second
```

**Payload size** is how many bytes travel in one request or response — here, each feed response is ~20 KB. Multiplying it by QPS answers “how much network throughput must I provision?”, i.e. **bandwidth**:

```text
Bandwidth = QPS × payload size
          = 1,734 × 20 KB
          ≈ 34.7 MB/second at peak
```

That single number tells you whether one server's network interface is enough or whether you need a CDN or fan-out across many hosts.

**Storage** answers a different question — not "traffic right now" but "how much disk will this consume over time?" It multiplies how many records you keep, how large each one is, how long you retain them, and how many copies you store for durability. Assume this app also has **1 million new photos uploaded per day**, each about 500 KB:

```text
Storage = records × record size × retention × replicas
        = 1,000,000 photos/day × 500 KB × 30-day retention × 3 replicas
        ≈ 45 TB
```

Finally, **concurrency** is how many requests are in flight at once — the number your connection pools and thread counts must support. It comes from Little's Law: throughput multiplied by how long each request takes to complete:

```text
Concurrency ≈ throughput × latency in seconds
            = 1,734 requests/second × 0.2 seconds
            ≈ 347 concurrent requests
```

![Capacity estimation derived from user behavior](assets/topic-01/capacity_estimation.png)

Estimates should be rounded, unit-consistent, and tied to a consequence such as caching, partitioning, connection limits, or capacity headroom. If a number cannot move one of those decisions, it is not worth computing.

---

## 3. Important concepts

### Requirement types

| Type | Question | Examples |
|---|---|---|
| Functional | What must the system do? | Create, read, update, notify |
| Non-functional | How well must it behave? | p99 latency, availability, durability |
| Constraint | What boundary must be respected? | Residency, legacy integration, deadline |
| Out of scope | What are we deliberately excluding? | Admin UI, analytics queries |

### Quality attributes

| Attribute | Meaning | Interview prompt |
|---|---|---|
| Latency | Time per operation | Which percentile and operation? |
| Throughput | Work per second | Average or peak? Read or write? |
| Availability | Ability to serve requests | What failure must be tolerated? |
| Durability | Protection from acknowledged-data loss | Can an accepted write be lost? |
| Consistency | Versions readers may observe | Is stale data acceptable here? |
| Security | Protection across trust boundaries | Who can perform each operation? |
| Cost | Resource and operational spend | What dominates at 10× scale? |

### High-leverage clarification questions

1. Who are the users, and what are the top two or three use cases?
2. What is explicitly out of scope?
3. What are current, peak, and projected traffic levels?
4. Which paths prioritize consistency, availability, or latency?
5. What are the retention, security, privacy, and residency constraints?
6. Is this greenfield, or must it coexist with an existing system?
7. What is the expected growth over the next year or two — is today's design meant to survive 10× traffic, or is this a v1 that will be revisited?
8. What does success look like to the business, and are there any hard deadlines, budget limits, or team/operational constraints shaping the solution?

### Minimum capacity worksheet

| Estimate | Why it matters |
|---|---|
| Peak read/write QPS | Compute, storage topology, connection limits |
| Read/write ratio | Cache and replica usefulness |
| Payload sizes | Network and serialization cost |
| Data growth and retention | Storage, partitioning, backup windows |
| Working set | Whether useful data can fit in memory |
| Fan-out | Hidden downstream traffic multiplication |
| Failure headroom | Ability to survive host or zone loss |

!!! warning "Avoid decorative arithmetic"
    If an estimate cannot affect a decision, skip it. Twelve decimal places of QPS will not rescue an unjustified architecture.

---

## 4. Decision and trade-off tables

![Decision process from requirement to evolution](assets/topic-01/decision_framework.png)

Use this sentence structure:

> Given **requirement X** and **estimate Y**, choose **A** over **B** because it improves **C**. It costs **D**. Validate it using **E**, and evolve when **F** occurs.

### Common evolution choices

| Decision | Simple starting point | Scale-oriented option | Evolution trigger |
|---|---|---|---|
| Compute | Vertical scaling — run on one bigger box; simplest to build, reason about, and debug | Stateless horizontal scaling — add interchangeable instances behind a load balancer so no single host is special | CPU/memory saturation, or an availability target that requires surviving the loss of one instance |
| Data | One relational database — a single writer with strong consistency and easy joins across entities | Read replicas, partitioning/sharding, or a specialized store (search, time-series, graph) matched to the access pattern | Write QPS, data size, or an access pattern the relational model can no longer serve efficiently |
| Reads | Database reads on every request — no extra moving parts, always fresh | Cache (in-memory), CDN (edge/static), or read replicas to absorb read traffic away from the primary | Read latency exceeds target, or read load threatens the database's ability to serve writes |
| Work | Synchronous, in-request processing — the caller waits for the full result | Queue plus background workers, decoupling slow or optional work from the response path | Work is slow, not required for the response, or fans out to many downstream calls |
| Geography | Single region — lowest cost and operational complexity | Active-passive (standby takes over on failure) or active-active (multiple regions serve writes) | A recovery-time objective (RTO), a data-residency law, or unacceptable latency for distant users |

![Visual comparison of competing system quality attributes](assets/topic-01/quality_tradeoffs.png)

| Tension | Favor the left when… | Favor the right when… | Cost to discuss |
|---|---|---|---|
| Consistency vs availability | Stale or incorrect data causes real harm — e.g., an account balance or an inventory count that could oversell | Continuing to serve users matters more than perfect freshness — e.g., a social feed or a product recommendation | Coordination overhead (locking, consensus) if you pick consistency; the staleness window readers must tolerate if you pick availability |
| Reliability vs cost | Downtime has real financial, safety, or trust impact — e.g., checkout or payments | The workload is non-critical, low-traffic, or cheaply retried — e.g., an internal report or batch job | Extra redundancy (replicas, multi-AZ) if you pick reliability; a longer recovery time if you pick cost |
| Security vs performance | The data or action is sensitive — e.g., PII, credentials, or money movement | The path is public, low-risk, and latency-sensitive — e.g., serving a public product page | Additional checks, cryptographic overhead, and complexity if you pick security; residual risk if you pick performance |
| Simplicity vs flexibility | Requirements are stable and well understood today | Multiple use cases genuinely need different behavior — not just a hypothetical future one | Abstraction layers to design and maintain if you pick flexibility; rework later if you pick simplicity and requirements diverge |

There is no globally correct position. Choose per operation, based on product impact.

---

## 5. Failure scenarios

![Decision tree for reacting to a dependency failure](assets/topic-01/failure_response.png)

| Failure | Safe response | Guardrail |
|---|---|---|
| Non-critical dependency fails (e.g., a recommendation or personalization call enriching a response) | Queue the work for later, defer it, or drop it according to policy — the primary response must not fail because of it | A bounded queue so a backlog can't grow forever, and visibility into how much work is being dropped |
| Critical dependency is slow (e.g., the database behind a checkout) | Fail fast once a timeout budget is exceeded, or fall back to a safe, pre-approved default instead of hanging | An end-to-end timeout budget shared across the whole call chain, not reset at every hop |
| Cache fails or goes cold | Fall back to the origin store, but bound how many requests can hit it at once | A concurrency limit on the origin plus request coalescing, so one cache miss doesn't become a stampede |
| Durable store fails, or can't confirm a write | Reject the write rather than pretend it succeeded | Never acknowledge a write to the caller unless it is actually durable |
| Queue consumers lag | Scale out consumers, or intentionally shed the least important events first | A lag alert plus enough retention headroom to catch up without losing data |
| Zone fails | Shift traffic to the surviving zones or regions | N+1 capacity provisioned ahead of time, and a failover path that has actually been tested, not just diagrammed |

For each dependency, state:

- timeout and retry owner;
- idempotency and duplicate behavior;
- queue, pool, and concurrency bounds;
- fallback validity and maximum staleness;
- detection, recovery, and reconciliation steps.

---

## 6. One focused worked example

### URL shortener

**The prompt you actually get:** “Design a URL shortener.” That is the entire brief — one deliberately vague sentence. Everything below is the work of turning it into something specific enough to design against, and the first few minutes belong to questions, not boxes and arrows.

**Questions to ask before designing anything**

Each one either pins down a requirement or rules something out of scope:

1. Who creates links, and who follows them — internal tool or public service? Decides whether we need auth, rate limiting, and abuse protection.
2. How many links per month, and how many clicks per link? This read/write ratio drives most of the architecture.
3. System-generated codes only, or custom aliases like `/spring-sale`? Aliases add uniqueness checks, conflicts, and squatting.
4. Do links expire — fixed TTL, user-specified date, or never? Decides whether we need a cleanup path and whether storage grows forever.
5. How fast must a redirect be, and what breaks if redirects are down? A slow redirect looks the same as a broken link, so this sets latency and availability targets.
6. Must a new link work instantly, or is a brief 404 acceptable? The read-after-write question — it decides whether reads can come from lagging replicas.
7. Are click analytics needed, and must they be real time? Decides whether analytics sits on the redirect path or behind a queue.
8. Any safety or compliance needs — malicious-URL scanning, residency, takedowns? Cheap to plan for, expensive to retrofit.

**Scope:** create a short link, redirect a short code to the original URL, and expire links once their lifetime passes. Analytics dashboards and customer-owned domains are out of scope — though click events are still collected asynchronously, so reporting can be added later without touching the redirect path.

**Targets:** redirects are the critical path — highly available, p99 under 100 ms, since a slow redirect is indistinguishable from a broken link. Link creation is low volume but must be durable: once the API returns a short code, that code can never be lost. New links also need read-after-write behavior, because the creator is usually the first person to click.

**Assumptions**

None of these numbers come from the prompt — they are estimates you state out loud so the interviewer can correct them before you build on top of them. The shape that matters is write-once, read-many: a link is created once but clicked many times, so reads dominate writes by a wide margin.

```text
20 million new links/month        (write volume)
100 redirects per link creation   (read/write ratio — reads dominate)
10× peak factor                   (busiest second vs. the daily average)
700 bytes stored per link         (long URL, short code, owner, timestamps)
5-year retention, 3 replicas      (how long links live, and copies kept for durability)
```

**Derived scale**

With the assumptions stated, the numbers follow mechanically — spread the monthly volume across seconds, then multiply outward to reach peak load and total storage:

```text
Average creates/s ≈ 20M / 2.6M ≈ 8        (≈2.6M seconds in a 30-day month)
Peak creates/s ≈ 80                        (8 × 10× peak factor)
Peak redirects/s ≈ 8 × 100 × 10 ≈ 8,000    (creates × redirect ratio × peak factor)
Replicated storage ≈ 20M × 12 × 5 × 700 B × 3 ≈ 2.5 TB
                     (links/month × months/year × years retained × bytes × replicas)
```

The headline number here is **8,000 peak redirects per second against roughly 80 peak creates per second** — a two-orders-of-magnitude gap between reads and writes. That single ratio is what justifies putting a cache in front of redirects instead of spending effort optimizing the write path, and it is worth saying explicitly rather than leaving the interviewer to infer it. The storage figure matters for a different reason: at roughly 2.5 TB replicated over five years, this comfortably fits on a single well-provisioned database, so sharding would be complexity without a requirement behind it.

![URL shortener architecture](assets/topic-01/url_shortener_architecture.png)

| Choice | Optimizes for | Costs / risks |
|---|---|---|
| Stateless API | Horizontal scaling and easy replacement — any instance can serve any request | State moves to shared dependencies (store, cache), so those must scale instead |
| Cache-aside redirects | Low latency and far lower load on the durable store, since 8,000 reads/s would otherwise all hit it | Staleness between cache and store, hot keys on viral links, and a cold-cache stampede on failure |
| Durable link store | Correct, acknowledged writes — a create is never lost once confirmed | Higher write latency than an in-memory or eventually-consistent option |
| Async click analytics | Redirects stay fast and resilient even if analytics is degraded or backed up | Analytics lag, and possible duplicate or out-of-order click events |
| Single region initially | Simplicity and lower cost — no cross-region coordination to design or operate | A full regional outage takes the service down, and distant users see extra latency |

**Failure walk-through:** during a store outage, cached redirects can keep serving correctly for links that are already warm in the cache, so most traffic continues to work even while the database is unreachable. Link creation, by contrast, must fail loudly and return an error rather than silently accept a write it cannot durably confirm — handing back a short code that was never persisted is far worse than refusing to create one. Analytics delays are acceptable by design and must never block or slow down a redirect, which is exactly why click events go through a queue instead of being written inline. Finally, a single viral short code can turn into a hot key that overwhelms one cache shard even while total QPS looks unremarkable; mitigating that needs request coalescing so concurrent misses collapse into one origin read, a short per-key TTL, or promoting that link into an edge/CDN cache closer to users.

---

## 7. Final revision checklist

```text
[ ] CLARIFY users, use cases, constraints, and out-of-scope items
[ ] QUANTIFY peak QPS, ratio, payloads, storage, concurrency, headroom
[ ] DEFINE minimal APIs/events, entities, and access patterns
[ ] DRAW read, write, async, and trust-boundary paths
[ ] DEEP-DIVE the largest scale, correctness, and failure risks
[ ] EXPLAIN timeouts, retries, bounds, degradation, and recovery
[ ] DEFEND each choice: optimizes, costs, validates, evolves
[ ] CLOSE with requirements met, biggest risk, and 10× evolution
```

!!! success "The senior-level finish"
    Summarize the architecture, identify its first likely bottleneck, explain degraded behavior, and name the metric or trigger that would justify the next layer of complexity.
