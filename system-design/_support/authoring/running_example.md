# Running example: Walmart International cart, checkout, order, and payment

Authoring reference, not a reader page (excluded from the MkDocs build).
Use it so every topic tells the same story with the same numbers. Bring in
multi-country detail **only where it changes a decision in that topic**.

## The platform

- **Services:** Cart, Checkout, Payment, Order (plus a Submitted-orders queue).
- **Countries:** Mexico, Canada, Chile, South Africa.
- **Deployment model:** one single-region deployment per country, running the
  same code. No cross-country traffic on the request path. This keeps Basics
  "single-region" (see README) and leaves multi-region to Advanced 15.
- **Sizing basis:** Mexico, the largest market. The other three are smaller
  copies; derive their numbers from their own DAU only if a topic needs it.

## Architecture (as drawn in Basics 1)

```text
Client -> Load balancer -> Cart service -> Cart cache (30-day TTL)
Load balancer -> Checkout service
Checkout -> Cart service            (read cart; checkout calls cart, never the reverse)
Checkout -> Payment service -> Payment gateway (external)
Checkout -> Submitted-orders queue  (publish only after payment is authorized)
Order service -> queue              (one of several subscribers; post-order is out of scope)
```

Diagram convention: arrows point from the caller to the service it calls.

| Data | Owner | Retention |
|---|---|---|
| Cart | Cart service | 30-day TTL |
| Order | Order service | Per country's tax law (Mexico: 5 years) |
| Payment | Payment service | Per country's tax law (Mexico: 5 years) |

## Mexico sizing (canonical numbers, used in Basics 1)

| Input | Value |
|---|---|
| Daily active shoppers | 9 million |
| Cart actions | 1.2 billion / month (avg 480 writes/s) |
| Cart reads per action | 8 (avg 3,840/s) |
| Completed checkouts | 10 million / month (avg 4/s, ~330K/day) |
| Peak factor | 10x (El Buen Fin); quincena is a recurring 2-3x |
| Peak cart reads / writes / checkouts | 38,400 / 4,800 / 40 per second |
| Cart storage | ~160-325 GB (bounded by TTL) |
| Order + payment storage | ~4-8 TB over 5 years (needs partitioning) |
| Servers | ~42 cart; checkout 2 by math, 3+ for availability |
| Inventory practice example | ~3,000 locations, 450 writes/s avg |

## Per-country facts

Mexico rows are already used in the docs. Everything marked **verify** must be
checked against a current source before it appears in a published topic.

| | Mexico | Canada | Chile | South Africa |
|---|---|---|---|---|
| Walmart business | Walmart de Mexico (Supercenter, Bodega Aurrera, Sam's Club) | Walmart Canada | Walmart Chile (Lider, Acuenta) | Massmart (Makro, Builders) |
| Currency | MXN | CAD | CLP (**no minor unit**) | ZAR |
| Sales tax | IVA 16% | GST 5% + provincial PST/HST | IVA 19% | VAT 15% |
| Big peak | El Buen Fin (Nov, Revolution Day weekend) | Black Friday, Boxing Day | CyberDay, Black Friday | Black Friday |
| Payday rhythm | Quincena (15th, month-end) | Bi-weekly | Month-end | Around the 25th (**verify**) |
| Tax-record retention | 5 years (CFF Art. 30) | 6 years (CRA) | 6 years (**verify**) | 5 years (SARS; **verify** Companies Act) |
| Data-protection law | LFPDPPP | PIPEDA (+ Quebec Law 25) | Ley 19.628 / Ley 21.719 | POPIA |
| Local payment methods | OXXO cash vouchers, cards | Interac, cards | Webpay (Transbank), cards | Cards, instant EFT |

## Where multi-country belongs in later topics

| Topic | The multi-country angle worth teaching |
|---|---|
| Basics 5: Architecture & Service Decomposition | Shared code, per-country deployments; what is global (catalog?) vs local (orders, payments). |
| Basics 7: API Design & Service Communication | Country in the request context (header or host) vs in every payload. |
| Basics 11: Data Modeling | `Money` minor units: CLP has none, so `cents` is a misleading name. Generic `tax` lines for IVA/GST/HST/VAT. |
| Basics 12: Partitioning | Country as the first partition key, then date or customer ID inside a country. |
| Basics 14: Availability & Deployment | Country-by-country rollouts as natural canaries (start with the smallest market). |
| Basics 15: Distributed ID Generation | Per-country counters collide (`ORD-0000000001` exists in all four). Fix with a country prefix or a global scheme. |
| Advanced 9: Rate Limiting | Per-country quotas so one country's sale event cannot starve another on shared infrastructure. |
| Advanced 15: Single vs Multi-Region | Per-country regions; failover within a country vs never across borders. |
| Advanced 16: Data Migration | Onboarding a new country onto the platform without downtime. |
| Advanced 19: Multi-Tenancy | Country as tenant: isolation, noisy neighbours (El Buen Fin vs Canadian Black Friday), fairness. |
| Advanced 20: Security & Privacy | Data residency under LFPDPPP, PIPEDA, Chilean law, and POPIA; cross-border transfer rules. |

## Open threads in Basics 1-3

- Docs 2-3 still show `CheckoutService` using a Stripe adapter directly. In the
  Basics 1 architecture, gateway adapters live inside the Payment service, and
  checkout uses a Payment-service client behind `PaymentProcessor`.
- `cart_checkout_degraded.png` (Payment service down) is rendered but not
  referenced by any doc yet. Natural home: Basics 1 "Fail" phase or Basics 14.
- Basics 2 is ~690 lines, over the 600-line guideline.
