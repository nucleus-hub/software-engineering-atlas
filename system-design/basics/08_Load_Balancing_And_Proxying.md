# Load Balancing & Proxying

## Terms to know before you start

You do not need to memorize these. Come back to this table whenever a term feels unfamiliar.

| Term | What it means in plain words |
|---|---|
| **Load balancer** | A machine or program with one address that spreads incoming requests over many servers, and stops sending to broken ones. |
| **Backend / upstream / pool** | The servers behind a load balancer. A **pool** (or *target group*) is one named set of them, such as "all Wallet API pods". |
| **Layer 4 (L4) load balancer** | Balances **connections**. It sees only IP addresses and ports, and forwards bytes without reading them. |
| **Layer 7 (L7) load balancer** | Balances **requests**. It reads HTTP, so it can route by path or header, retry, and add headers. |
| **Proxy (forward proxy)** | A middleman that acts **for clients**. The destination sees the proxy's address, not the client's. |
| **Reverse proxy** | A middleman that acts **for servers**. Clients think they are talking to the server, but they reach the proxy first. |
| **DNS load balancing** | Spreading users by giving different answers to the same name, such as several IP addresses or the nearest region's address. |
| **Anycast** | Announcing **the same IP address from many locations**, so the internet's routers deliver each user's packets to the nearest one. |
| **Health check** | A small, regular request the load balancer sends to each server to ask, "are you able to serve?" |
| **Outlier detection** | Removing a server because its *real* responses look bad, such as five errors in a row, without waiting for a health check. |
| **Connection draining** | Letting a server finish its in-flight requests before it is removed, instead of cutting them off. |
| **Sticky session (session affinity)** | Always sending the same user to the same server. [Basics 5](05_Architecture_Styles_And_Service_Decomposition.md#3-stateless-vs-stateful-services) explained why it hurts. |
| **Egress proxy** | A forward proxy that all of *your* outgoing calls pass through, so they leave from a few known addresses. |
| **Envoy, Nginx, HAProxy** | Popular proxy programs. Each can be a reverse proxy, a load balancer, or both. |
| **Sidecar / service mesh** | A proxy, often Envoy, running next to every service instance. Together, all the sidecars form a **service mesh**. |
| **NAT** | A router that lets many devices share one public IP address. Mobile networks put thousands of phones behind one. |

??? info "Java and Spring features used on this page (open if they are new to you)"
    - **`ManagedChannelBuilder`** builds a gRPC client connection. `forTarget("dns:///...")` tells it to look up every address behind a name, and `defaultLoadBalancingPolicy("round_robin")` spreads calls over all of them.
    - **`NettyServerBuilder.maxConnectionAge(...)`** makes a gRPC server politely close each client connection after a while, so clients reconnect and notice new servers.
    - **`server.forward-headers-strategy`** tells Spring Boot to trust headers like `X-Forwarded-For` from the proxy in front of it, so the app sees the real client's IP address.
    - **`server.shutdown=graceful`** makes Spring Boot stop accepting new requests on shutdown, and wait for in-flight ones to finish.

---

## 1. Why balance load, and the new running example

One server has limits: CPU, memory, connections, and the fact that it will one day crash or be redeployed. A load balancer hides many servers behind **one address** and does four jobs:

| Job | What it means |
|---|---|
| **Spread the work** | Send each connection or request to a server that can take it. |
| **Hide failures** | Notice a broken server and stop sending to it. |
| **Allow change** | Add, remove, and replace servers without clients noticing. |
| **Guard the door** | End TLS, reject oversized requests, and keep one noisy kind of traffic from starving another. |

**The new running example: a digital wallet.** The URL shortener had almost no state, so it could not show what happens when money is involved. From this topic onwards, every page uses one simple wallet. Users **top up** from a card or bank, **pay** merchants, **send** money to friends, and **withdraw** to their bank. Three services do the work:

| Service | What it does | Who calls it |
|---|---|---|
| **Wallet API** | Public REST API for the app and merchants. | Phones, merchant checkouts, and the card network's top-up callbacks |
| **Ledger** | The source of truth for money. Every transfer is one entry with a debit and an equal credit, so the books always sum to zero. | The Wallet API, over gRPC |
| **Payouts** | Sends withdrawals to the user's bank. | The Ledger, through a queue |

When Asha sends Ravi **$25**, the Ledger writes one entry: debit Asha's wallet $25, credit Ravi's wallet $25. Nothing is ever edited. A mistake is fixed with a new, reversing entry.

**The numbers, fixed for every topic:** 10 million users, about **500 transfers per second** normally and **5,000 at peak**, and balance checks about ten times as often as transfers. One big merchant, the coffee chain BeanCo, receives 5% of all payments.

Peak traffic at the Wallet API is about 50,000 balance reads plus 5,000 transfers, so **55,000 requests per second**. If one pod handles about 2,000 per second, that is 28 pods. The pods run in three zones, and the wallet must survive losing one, so the other two zones must hold all 28: 14 per zone, **42 pods** in total. Something has to spread traffic over those 42 pods, and that is this page. It answers five requests:

| Request | Who asked | Section |
|---|---|---|
| Spread 55,000 requests per second over 42 Wallet API pods, and choose the right kind of load balancer. | Platform team | 2 |
| The Ledger grew from 6 to 12 pods, but the 6 new pods receive no traffic at all. | Ledger team | 2 |
| The bank only accepts payout calls from two registered IP addresses. | Payouts team | 3 |
| One slow Ledger pod makes every user's transfer slow. | On-call engineer | 4 |
| Deployments cause a burst of errors, and a new Ledger version must start with 1% of traffic. | Release team | 5 |

!!! tip "The decision in one sentence"
    Use a Layer 7 load balancer for HTTP and gRPC, spread work by how busy each server is rather than by turns, keep each kind of traffic in its own pool, and treat health checks, draining, and retries as part of the design, not as settings.

---

## 2. Types: DNS, Layer 4, and Layer 7

The "layer" is how much of the request the load balancer reads before it decides. Reading more lets it make smarter decisions, but costs more work. [Basics 4](04_Networking_And_Request_Lifecycle.md#2-the-network-one-layer-at-a-time) introduced the layers.

![What each load balancer sees. Layer 4 sees only a source and destination address and port, plus encrypted bytes, and picks a server once per TCP connection. Layer 7 ends TLS, reads the method, path, and headers, and picks a server for every request, sending /v1/ to the Wallet API pool and /webhooks/ to the webhook pool](assets/topic-08/l4_vs_l7.png)

### Layer 4: balancing connections

A Layer 4 load balancer sees a new TCP connection arrive, picks a server, and from then on copies bytes in both directions. It never reads them, so it does not care whether they are HTTP, gRPC, a database protocol, or encrypted.

- **What it gives you:** it is very fast and cheap, it can handle millions of connections, it works for any protocol, and it can pass TLS through untouched.
- **What it costs:** it decides **once per connection**. Every request on that connection goes to the same server. It cannot route by path, cannot retry a failed request, and cannot add headers, because it never sees a request.

### Layer 7: balancing requests

A Layer 7 load balancer ends the client's connection (and usually its TLS, as in [Basics 4](04_Networking_And_Request_Lifecycle.md#tls-https-and-where-encryption-ends)), reads each HTTP request, and opens or reuses a **separate** connection to the chosen server.

- **What it gives you:** a decision **per request**. It can route `/v1/` and `/webhooks/` to different pools, retry a request that never reached a server, add `X-Request-Id`, and enforce timeouts, size limits, and rate limits.
- **What it costs:** more CPU per request, about a millisecond of extra latency, TLS certificates to manage, and one more component in the request path that can have bugs.

### DNS and Anycast: choosing the front door

Before any load balancer is reached, DNS already chose an address. **DNS load balancing** returns several addresses for one name, or a different address depending on where the user is, or only the addresses that pass a health check. It is cheap, but it is coarse: resolvers cache answers for the TTL ([Basics 4](04_Networking_And_Request_Lifecycle.md#dns-turning-a-name-into-an-address)), clients keep using the address they got, and DNS knows nothing about how busy each server is. Use it to pick a **region or a load balancer**, never a server.

**Anycast** goes one step further: the same IP address is announced from many sites, and the internet's routers carry each user's packets to the nearest site. CDNs and large DNS providers use it. A flood of attack traffic is spread over every site instead of hitting one, and a distant user's TLS handshake ends nearby. Anycast mostly lives at the edge networks you rent, not in your own data centre.

| | DNS | Layer 4 | Layer 7 |
|---|---|---|---|
| **Decides** | Once per lookup, then cached | Once per connection | For every request |
| **Can see** | Only the name being looked up | IP addresses and ports | Method, path, headers, cookies |
| **Reacts to a dead server** | Slowly: only when caches expire | In seconds | In seconds, and can retry elsewhere |
| **Best for** | Choosing a region or a load balancer | Huge connection counts, non-HTTP protocols, TLS pass-through | HTTP and gRPC services |

**Large systems stack them.** DNS (sometimes Anycast) picks the site, a Layer 4 tier spreads connections over a fleet of Layer 7 proxies, and the Layer 7 proxies spread requests over the services. Each tier does the job it is cheapest at.

### The gRPC trap: one connection, thousands of requests

gRPC runs on HTTP/2, which sends **many requests over one long-lived connection** ([Basics 7](07_API_Design_And_Service_Communication.md#grpc-typed-calls-between-services)). That is great for speed, but it defeats Layer 4 balancing. This is exactly what happened to the wallet's Ledger:

![Requests per second on each Ledger pod. Left, behind a Layer 4 Kubernetes Service: 42 long-lived connections landed unevenly on the 6 original pods, three of them above the 8,000 per second capacity line, while the 6 new pods get nothing. Right, with per-request balancing: all 12 pods carry about 4,600 per second](assets/topic-08/grpc_pinning.png)

- Each of the 42 Wallet API pods opened **one** HTTP/2 connection to the Ledger, through a Kubernetes Service. A Kubernetes Service balances like Layer 4: it picks a pod once per connection.
- The 42 connections landed unevenly on the 6 original pods: 10 on one, 4 on another. At peak, each connection carries about 55,000 / 42 ≈ 1,300 requests per second, so the busiest pod gets about 13,000 per second when its limit is 8,000.
- The team added 6 pods. Existing connections never move, and nobody opens new ones, so **the new pods sit idle while the old ones overload**.

There are three fixes, from simplest to most thorough:

| Fix | How it works | Cost |
|---|---|---|
| **Limit connection age** | The Ledger closes each connection after, say, 5 minutes. Clients reconnect and land on any pod, including new ones. | Balance is only rough, and it takes minutes to catch up after scaling. |
| **Client-side balancing** | The gRPC client looks up *every* Ledger pod's address, keeps a connection to each, and spreads calls over them. | Every client language needs it configured correctly. |
| **A Layer 7 proxy** | An Envoy sidecar, or a gRPC-aware load balancer, picks a pod for every call. | One more component to run, but every service gets it the same way. |

In Java, client-side balancing is two lines. A Kubernetes **headless Service** makes DNS return every pod's address instead of one virtual address:

```java
ManagedChannel ledger = ManagedChannelBuilder
        .forTarget("dns:///ledger-headless.wallet.svc:9090")   // DNS returns every Ledger pod's address
        .defaultLoadBalancingPolicy("round_robin")            // spread calls over all of them, call by call
        .build();
// On the Ledger side: NettyServerBuilder.maxConnectionAge(5, TimeUnit.MINUTES), so clients
// reconnect regularly, look the name up again, and find pods that were added since.
```

!!! question "Practice: the note-taking app"
    The note-taking app wants three things: (a) send `/api/attachments/*` to a separate fleet built for large files; (b) put a load balancer in front of its PostgreSQL read replicas; (c) send European users to its EU region. Which type of load balancing fits each?

??? success "Answer"
    (a) **Layer 7**: routing by path means reading the request. (b) **Layer 4**: the PostgreSQL protocol is not HTTP, and each database connection is long-lived and should stay on one replica. (c) **DNS** (geo-based answers): this is choosing a region, which DNS does cheaply. Within each region, a Layer 7 load balancer takes over.

---

## 3. Proxies: forward, reverse, and the tools

A proxy is a middleman that receives a request and sends it on. The only question is **whose side it is on**.

![Forward vs reverse proxy. Left: the wallet's Payouts pods send bank calls through an egress proxy pair, so the bank sees only the two registered addresses 198.51.100.7 and .8. Right: phones call api.wallet.example, which reaches a reverse proxy that ends TLS, applies limits, and forwards to the Wallet API pods, which the phones never see](assets/topic-08/forward_vs_reverse_proxy.png)

### Forward proxy: acting for the clients

A forward proxy sits in front of **clients**. The destination only ever sees the proxy's address. Company networks use one so that every employee's web traffic leaves through a single, monitored exit.

In the wallet, the bank only accepts payout calls from **two registered IP addresses**. Payouts runs on many pods whose addresses change with every deployment, so all its calls go through an **egress proxy** pair with two fixed addresses. The proxy also:

- **holds the client certificate** for the mutual TLS connection the bank requires, so no Payouts pod needs it;
- **logs every outgoing call**, which auditors ask for in payment systems;
- **only allows known destinations**, so a bug or an attacker cannot make the wallet's servers call arbitrary internet addresses.

### Reverse proxy: acting for the servers

A reverse proxy sits in front of **servers**. Clients believe `api.wallet.example` is the server; they never learn how many pods are behind it. Besides balancing, a reverse proxy is the natural place to:

- **end TLS**, so certificates live in one place;
- **enforce limits** from [Basics 6](06_API_Correctness_Security_And_Resource_Design.md#limits-on-size-and-time): request size, header size, and timeouts;
- **buffer slow clients**: a phone on a weak network may take seconds to upload a request. The proxy collects it and hands the pod a complete request in one go, so a Java thread is not held hostage for seconds;
- **compress and cache** responses (Basics 9), and **rate-limit** callers (Advanced 9).

**Load balancer, reverse proxy, API gateway: what's the difference?** Mostly emphasis. A *load balancer* is a reverse proxy whose main job is spreading load. An *API gateway* is a reverse proxy that also understands your API: API keys, tokens, quotas, and per-route rules, as in Basics 6. One Nginx or Envoy instance can do all three jobs.

### The real client's address

Behind a proxy, every request appears to come from **the proxy's** address. The proxy adds the real address in a header, `X-Forwarded-For`. The wallet needs it for fraud checks and per-user limits, but there is a catch: **anyone can send that header**. Trust only the value added by *your* proxies, and only when the request really came from them. In Spring Boot, set `server.forward-headers-strategy=native` and list your proxies' addresses as trusted (`server.tomcat.remoteip.internal-proxies`).

### The tools you will hear about

| Tool | What it is best at |
|---|---|
| **Nginx** | A fast reverse proxy driven by a config file. Common at the edge and as a Kubernetes ingress. |
| **HAProxy** | A very fast, very configurable Layer 4 and Layer 7 load balancer. |
| **Envoy** | A proxy built for traffic *between* services. Its config can change through an API without restarts, it understands gRPC, and it is the sidecar in service meshes such as Istio. |
| **Cloud load balancers** | Managed and highly available, for example AWS NLB (Layer 4) and ALB (Layer 7). Nobody on your team runs the machines. |
| **Kubernetes Service and Ingress** | A *Service* balances connections like Layer 4. An *Ingress* (or the newer Gateway API) routes HTTP like Layer 7. |

Here is the wallet's public entry as an Nginx config, trimmed to the parts this page discusses:

```nginx
upstream wallet_api {
    least_conn;                                  # send to the pod with the fewest open requests
    server 10.0.1.11:8080 max_fails=3 fail_timeout=10s;
    server 10.0.2.11:8080 max_fails=3 fail_timeout=10s;
    # ...one line per pod; in Kubernetes, the ingress controller writes these for you
    keepalive 64;                                # reuse connections to the pods (Basics 4)
}
upstream topup_webhooks {                        # a separate, smaller pool
    server 10.0.1.40:8080;
    server 10.0.2.40:8080;
}
server {
    listen 443 ssl;
    server_name api.wallet.example;
    client_max_body_size 64k;                    # a transfer is tiny; reject anything bigger here

    location /v1/ {
        proxy_pass http://wallet_api;
        proxy_http_version 1.1;                  # needed for keepalive to the pods
        proxy_set_header Connection "";
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-Id $request_id;
        proxy_read_timeout 2s;
        proxy_next_upstream error timeout;       # Nginx never retries a POST unless told to
    }
    location /webhooks/ {
        allow 192.0.2.0/24;                      # the card network's published addresses
        deny all;
        proxy_pass http://topup_webhooks;
    }
}
```

!!! question "Practice: the note-taking app"
    The note-taking app's servers call an AI summarization vendor, which wants to allowlist the addresses calls come from. Separately, the app's rate limiter keys on `X-Forwarded-For`, and one user avoids it by sending a different made-up value with every request. What would you change?

??? success "Answer"
    Route all calls to the vendor through an **egress proxy** with fixed addresses, and give the vendor those addresses. For the rate limiter, make the edge proxy **overwrite** any incoming `X-Forwarded-For` (or take only the address its own proxy appended), and have the app trust the header only from the proxy's addresses. Never trust a value the client wrote itself.

---

## 4. Strategies: how the load balancer picks a server

Once a load balancer has a request and a pool, it needs a rule for choosing. The rule matters most **when servers are not identical**, and in production they never are: one pod is in the middle of a garbage-collection pause, one shares a busy machine, one just started.

![Three Ledger pods sharing 3,000 calls per second, where pod C has become five times slower (50 ms instead of 10 ms). Round-robin still gives C 1,000 calls per second, so a third of all calls are slow and the average is 23 ms. Least-request gives C only about 270, so 9% of calls are slow and the average is 14 ms](assets/topic-08/lb_strategies.png)

| Strategy | How it picks | Good for | Fails when |
|---|---|---|---|
| **Round-robin** | Takes turns: 1, 2, 3, 1, 2, 3... | Identical servers and similar, short requests. | One server is slow: it still gets its full share, as in the picture. |
| **Weighted round-robin** | Takes turns in proportion to weights, such as 2 : 1. | Servers of different sizes, and sending 1% to a new version. | The weights are guesses that nobody updates. |
| **Least connections / least request** | Sends to the server with the fewest requests in progress. | Requests whose duration varies, and servers that slow down. | A broken server answers errors in 1 ms, looks idle, and attracts most of the traffic (see below). |
| **Power of two choices** | Picks two servers at random and sends to the less busy one. | Large pools and many load balancers. It is nearly as good as least-request, and needs no global view. | Rarely; it is Envoy's default for least-request. |
| **IP hash** | Hashes the client's IP address, so a client always reaches the same server. | Keeping a client on one server. | Many users share one IP address, or servers are added. |
| **Consistent hashing on a key** | Hashes a chosen key, such as a user ID, onto a ring of servers. | Caches, where the same key should reach the same server. Basics 12 covers it. | One key is far hotter than the rest. |

**Why "fewest in progress" beats taking turns.** In the picture, pod C slows from 10 ms to 50 ms. Round-robin does not notice, so C keeps receiving a third of all calls, and a third of users wait five times longer. Least-request keeps the number of calls *in progress* about equal on every pod. A slow pod finishes calls slowly, so its count stays high and it receives fewer new calls: about 270 per second instead of 1,000. Only 9% of calls are slow, and nobody had to configure anything.

**The fast-failing pod.** Least-request has one dangerous blind spot. Suppose a Ledger pod loses its database connection and answers every call with an error **in 1 ms**. It always looks the least busy, so it attracts the most traffic. With two healthy pods at 10 ms, the broken one would receive about **83% of all calls**, and fail all of them. That is why least-request must always be paired with **outlier detection** (section 5), which removes a pod that keeps returning errors.

**Why IP hash is wrong for the wallet.** Mobile networks put thousands of phones behind one public address (carrier-grade NAT), so IP hash sends all of them to one pod. And with simple hashing, `hash mod 42`, adding a 43rd pod moves almost every client to a different pod. Consistent hashing moves only about 1 in 43. The wallet does not need either: the Wallet API is stateless, so any pod can serve any request.

**Hashing by merchant would create a hot pod.** If the wallet hashed payments by merchant ID, every BeanCo payment would land on one pod. BeanCo receives 5% of all payments, but a fair share among 42 pods is about 2.4%, so that pod would carry **twice its share**. Hot keys come back in Advanced 8.

**The wallet's choices:** least-request for the Wallet API and the Ledger, because transfer calls vary from 5 ms to 200 ms; plain round-robin for the small webhook pool, whose requests are all alike; and weights for canary releases (section 5).

!!! question "Practice: the note-taking app"
    The note-taking app's API has 10 identical servers behind a load balancer using round-robin. Most requests take 20 ms, but "export notebook as PDF" takes up to 8 seconds. Users complain that the app sometimes freezes for a few seconds. Explain why, and suggest two improvements.

??? success "Answer"
    Round-robin keeps sending fast requests to a server that is busy with several PDF exports, so they queue behind them. Switch to **least-request**, so busy servers receive fewer new requests. Better still, give exports **their own pool** (route `/api/export/*` separately), or make them asynchronous with `202 Accepted` as in Basics 7, so slow work can never queue in front of fast work.

---

## 5. Keeping the pool healthy: health checks, draining, and retries

A load balancer is only as good as its list of healthy servers. Four mechanisms keep that list honest.

**Active health checks.** The load balancer calls a small endpoint, such as `/health/ready`, on every pod every few seconds. In the wallet: every 5 seconds, out after 2 failures, back in after 3 successes. A dead pod stops receiving traffic within about 10 seconds. What the endpoint should check, and how readiness differs from liveness, is covered in **Basics 14 (Availability & Deployment Fundamentals)**.

**Passive health checks (outlier detection).** Real responses are better evidence than a probe. Envoy can remove a pod after **5 errors in a row** for 30 seconds, and doubles the time if it happens again. Two safety limits matter. Never remove more than a fixed share of the pool at once, such as 30%. And if most pods look unhealthy, Envoy spreads traffic over all of them anyway (its *panic threshold*), because a shared dependency is probably failing and refusing everything would only make it worse.

```yaml
# Envoy: the Wallet API's view of the Ledger (address and HTTP/2 settings trimmed)
- name: ledger
  lb_policy: LEAST_REQUEST          # power of two choices by default
  outlier_detection:
    consecutive_5xx: 5              # five errors in a row...
    base_ejection_time: 30s         # ...and the pod is out for 30 seconds
    max_ejection_percent: 30        # never remove more than 30% of the pool
```

**Draining on deployment.** When a pod is about to stop, the load balancer must first stop sending it **new** requests, and then let its **in-flight** requests finish. If the pod simply exits, every transfer it was handling fails mid-way, which is the burst of errors the release team saw. In Kubernetes and Spring Boot:

1. The pod is marked as terminating, and the load balancers start removing it. This takes a few seconds to reach every proxy, so the pod waits briefly (a `preStop` sleep of 5 to 10 seconds) while requests still arrive.
2. Spring Boot's `server.shutdown=graceful` stops accepting new requests and waits for in-flight ones, up to `spring.lifecycle.timeout-per-shutdown-phase=30s`.
3. Only then does the process exit.

**New pods need a gentle start.** A Java pod that has just started is slow until its code is compiled and its caches and connection pools are warm. Least-request sees an idle new pod and floods it. **Slow start**, supported by Envoy and most cloud load balancers, raises a new pod's share gradually over, say, 60 seconds.

**Weights for canary releases.** A new Ledger version first receives 1% of calls, with weights of 99 : 1, while the team compares its error rate and latency with the old version. Then 10%, 50%, 100%. Deployment strategies are covered in Basics 14; the load balancer's part is simply honouring the weights.

**Retries: only when it cannot double-charge.** A Layer 7 load balancer can retry a failed request on another pod. That is safe when the request **never reached** a pod (the connection was refused), or when it is idempotent, like `GET /v1/balance`. It is dangerous for `POST /v1/transfers`: if the first pod moved the money and then timed out, a retry could send Asha's $25 **twice**. The wallet lets the app retry instead, with the same `Idempotency-Key`, so the Wallet API recognizes the repeat. Idempotency is covered in Advanced 7, and retry storms in Advanced 10. Keep every retry inside the timeout budget from [Basics 4](04_Networking_And_Request_Lifecycle.md#timeout-budgets).

**The load balancer must not be a single point of failure.** A managed cloud load balancer already runs in every zone. A self-run Nginx or HAProxy needs at least two instances: either a floating address that moves to the standby when the active one dies, or a Layer 4 tier or several DNS addresses in front.

!!! question "Practice: the note-taking app"
    Every time the note-taking app deploys, users see about 20 seconds of `502 Bad Gateway` errors, even though the new version starts quickly. What is probably happening, and what three settings would you check?

??? success "Answer"
    The old pods exit while the load balancer still sends them requests, and their in-flight requests are cut off. Check: (1) a short **`preStop` delay**, so the load balancer stops sending before shutdown begins; (2) **graceful shutdown** in the app (`server.shutdown=graceful` with a timeout), so in-flight requests finish; (3) the load balancer's **draining time** (deregistration delay), which must be at least as long as the app's longest normal request.

---

## 6. Putting it together: the wallet's front doors

![The wallet's load balancing. Phones and merchant checkouts resolve api.wallet.example to load balancer addresses in three zones. A Layer 7 load balancer sends /v1/ to 42 Wallet API pods using least-request, and /webhooks/ from the card network's addresses to a separate pool of 4 webhook pods. Each Wallet API pod calls the Ledger's 12 pods through an Envoy sidecar using least-request, outlier detection, and a 1% canary. The Ledger hands withdrawals to Payouts, whose calls leave through an egress proxy pair with two fixed addresses registered with the bank](assets/topic-08/wallet_front_doors.png)

Every hop uses the simplest balancing that does the job:

| Hop | Type | Strategy | Why |
|---|---|---|---|
| Phone → `api.wallet.example` | **DNS**, one address per zone | Health-checked answers | Chooses a working zone. Pods are chosen later. |
| Edge → Wallet API pods | **Layer 7** (managed, or Nginx) | Least-request, slow start | Routes by path, ends TLS, enforces limits, and avoids slow pods. |
| Card network → webhook pods | **Layer 7**, separate pool | Round-robin, address allowlist | A rush of app traffic can never delay top-up confirmations. |
| Wallet API → Ledger (gRPC) | **Layer 7 sidecar** (Envoy) | Least-request, outlier detection, 99 : 1 canary | Balances per call, not per connection, so new Ledger pods get traffic at once. |
| Payouts → bank | **Egress proxy** pair | Active and standby | The bank sees only two registered addresses, and the wallet's client certificate for the bank lives in one place. |

**One flow, end to end.** Asha sends Ravi $25:

1. Her phone looks up `api.wallet.example` and gets the load balancer's addresses in three zones. It connects to one and finishes the TLS handshake there.
2. The load balancer reads `POST /v1/transfers`, checks the body is under 64 KB, adds `X-Request-Id` and `X-Forwarded-For`, and sends the request to the least-busy Wallet API pod, pod 17.
3. Pod 17 checks Asha's token, then calls `Ledger.Transfer` through its Envoy sidecar. Envoy picks two Ledger pods at random and chooses the one with fewer calls in progress. One time in a hundred, that is the canary.
4. The Ledger writes the entry, debit Asha $25 and credit Ravi $25, and replies. Pod 17 returns `201 Created` to the phone through the load balancer.

**When things go wrong:**

| Event | What protects the wallet |
|---|---|
| A Wallet API pod crashes in the middle of Asha's transfer. | The load balancer does **not** retry the `POST`. The app retries with the same `Idempotency-Key`, the load balancer picks another pod, and the money moves once. |
| A Ledger pod slows down during a long garbage-collection pause. | Least-request sends it fewer calls at once. If it starts failing, outlier detection removes it for 30 seconds. |
| A Ledger pod loses its database and fails every call in 1 ms. | Outlier detection removes it after 5 errors, before it can attract most of the traffic. |
| A whole zone goes down. | DNS and the load balancer stop using that zone, and the remaining 28 pods carry the peak, because the fleet was sized for this. |
| A deployment replaces all 42 pods. | Each pod drains: it stops receiving new requests, finishes its in-flight transfers within 30 seconds, and only then exits. |
| A promotion brings ten times the usual app traffic. | It queues in the Wallet API pool only. Top-up callbacks have their own pool and keep flowing. |
| The active egress proxy dies. | The standby takes over its address. The bank still sees one of the two registered addresses. |

!!! tip "The headline to say out loud"
    "DNS picks a healthy zone. A Layer 7 load balancer routes by path and sends each request to the least-busy pod, with separate pools so one kind of traffic can't starve another. Internal gRPC is balanced per call, not per connection. Outgoing calls leave through an egress proxy with fixed addresses. And health checks, draining, slow start, and idempotent retries let pods fail and be replaced without users noticing."

---

## 7. Common beginner mistakes

- **Drawing one box labelled "load balancer"** without saying whether it is Layer 4 or Layer 7, or what strategy it uses.
- **Putting gRPC behind a Layer 4 load balancer** or a plain Kubernetes Service, then wondering why new pods sit idle.
- **Using round-robin when requests vary**, so fast requests queue behind slow ones on a busy server.
- **Using least-request without outlier detection**, so a pod that fails instantly receives most of the traffic.
- **Using IP hash for mobile users**, who share addresses behind carrier NAT.
- **Letting the load balancer retry `POST` requests** that move money or create things.
- **Trusting `X-Forwarded-For` from anyone.**
- **Sending every kind of traffic to one pool**, so a spike of one kind starves the others.
- **Forgetting draining and slow start**, so every deployment shows up as an error spike.
- **Running one self-managed load balancer**, which becomes the single point of failure it was meant to remove.
- **Balancing between servers with DNS**, then waiting hours for caches to forget a dead one.

---

## 8. Test yourself

These three problems increase in difficulty. Try each one on paper before opening the answer.

!!! question "Problem 1 (warm-up): pick the balancing"
    Choose a load balancing type and strategy for each: (a) a fleet of 20 identical servers serving a public website's HTML pages; (b) 8 Redis cache servers, where each key should always reach the same server; (c) a pool of MQTT brokers holding 2 million long-lived connections from delivery scooters; (d) sending users to the nearest of three regions.

??? success "Answer"
    (a) **Layer 7, round-robin or least-request**: requests are short and similar, and Layer 7 also gives you TLS, limits, and caching. (b) **Consistent hashing on the key**, usually done by the client library: adding a ninth server moves only about one key in nine. (c) **Layer 4, least connections**: it is not HTTP, connections last for hours, and the load is the number of open connections. (d) **DNS** with geo-based or latency-based answers, ideally with health checks so a dead region drops out.

!!! question "Problem 2 (diagnosis): the uneven order service"
    The food-delivery company's checkout service calls its order service over gRPC through a Kubernetes Service. Before a holiday, the team scaled the order service from 4 to 8 pods. On the day, the 4 old pods ran at 95% CPU and the 4 new pods at 5%. The team also uses IP hash at the edge, and one pod is always busier than the rest, because a big corporate customer orders lunch for its whole office from one address. And every deployment produced a burst of `503` errors. Find each cause and its fix.

??? success "Answer"
    | Problem | Cause | Fix |
    |---|---|---|
    | New pods idle, old pods overloaded | The checkout pods' HTTP/2 connections were opened before scaling. A Kubernetes Service picks a pod per **connection**, and those connections never move. | Balance per call: an Envoy sidecar or client-side `round_robin` over a headless Service. Add `maxConnectionAge` on the server, so clients reconnect regularly. |
    | One pod always busier | IP hash sends every employee behind the office's single address to the same pod. | Use least-request. The service is stateless, so it never needed affinity. |
    | `503` errors on every deployment | Pods exit while still listed in the load balancer, and in-flight requests are cut off. | A `preStop` delay, graceful shutdown, and a draining time at least as long as the slowest normal request. Add slow start, so new JVMs are not flooded while they warm up. |

!!! question "Problem 3 (design): the note-taking app goes collaborative"
    The note-taking app adds live co-editing: everyone editing the same note shares a WebSocket connection to a collaboration server, which keeps that note's live state in memory. There will be up to 400,000 open connections. Design the load balancing: the balancer type, how to choose a server, what happens on deployment, and what happens when a server dies.

??? success "Answer"
    | Concern | Design |
    |---|---|
    | **Balancer type** | **Layer 7**, because it must read the WebSocket upgrade request, check the session, and look at the note ID in the path. Its idle timeout must be longer than the app's heartbeat, such as a 30-second ping. |
    | **Choosing a server** | **Consistent hashing on the note ID**, so everyone editing the same note reaches the server holding that note's state. Hashing by user would scatter one note's editors over several servers. Use least connections only for a new note's first connection, if the state can live anywhere. |
    | **Capacity** | Plan by **open connections**, not requests per second: at 20,000 connections per server, 400,000 connections need 20 servers, plus room for one zone to fail. |
    | **Deployment** | Draining could take hours, so give servers a deadline instead. The server saves each note's state and closes its connections with a "reconnect" message. Clients reconnect after a **random 1 to 10 second delay**, so they do not all arrive at once. |
    | **A server dies** | Consistent hashing moves only that server's notes to the others. Clients reconnect and reload the note from its last saved state, so the server must save edits regularly, never only in memory. |

    A good follow-up: how consistent hashing places keys, and what happens when a server joins or leaves, is covered in **Basics 12 (Data Partitioning, Sharding & Replication)**.

---

## 9. Key takeaways

- **A load balancer does four jobs.** It spreads work, hides failures, allows change, and guards the door. The wallet needs 42 Wallet API pods to carry 55,000 requests per second and survive a lost zone, and none of that works without one.
- **The layer decides what the balancer can see.** DNS chooses a region or a load balancer, Layer 4 balances connections for any protocol, and Layer 7 balances requests and can route by path. Large systems stack all three.
- **gRPC behind a Layer 4 balancer is a trap.** HTTP/2 sends thousands of calls over one connection, so the Ledger's 6 new pods sat idle while old ones hit 13,000 calls per second. Balance per call with a sidecar or client-side balancing, and limit connection age.
- **A forward proxy acts for clients, and a reverse proxy acts for servers.** The wallet's egress proxy gives the bank two fixed addresses. Its reverse proxy ends TLS, enforces limits, and buffers slow phones.
- **Trust `X-Forwarded-For` only from your own proxies.** Anyone can write the header, and fraud checks and rate limits depend on it.
- **Balance by how busy servers are, not by taking turns.** When one pod became five times slower, round-robin made a third of calls slow, and least-request made only 9% slow.
- **Least-request always needs outlier detection.** A pod that fails in 1 ms looks idle and would receive about 83% of calls.
- **Use affinity only when there is state.** IP hash breaks behind carrier NAT. When you do need affinity, use consistent hashing on a meaningful key, and watch for hot keys like BeanCo.
- **Separate pools stop one kind of traffic from starving another.** Top-up callbacks keep flowing during a promotion because they never share a queue with app traffic.
- **Deployments are a load balancing problem.** Health checks, draining, slow start, and weights make 42 pod replacements invisible to users. The balancer may retry a `POST` only if it never reached a pod; otherwise the client retries with an `Idempotency-Key`.
- **In interviews, never draw a bare "LB" box.** Say which layer it is, what strategy it uses, how it learns a server is unhealthy, and what happens during a deployment. Answering "what happens to an in-flight request?" well signals real experience.
