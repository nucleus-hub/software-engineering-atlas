#  Docs — Roadmap, Conventions & Glossary

Central place for cross-cutting documentation that doesn't belong to a single discipline.

## Contents
- **Learning Roadmap** (below)
- **Conventions** (naming, commits, testing expectations)
- **Glossary** (grow this as you learn)

---

##  Learning Roadmap (detailed)

### Phase 1 — Foundations
- Java language core (collections, generics, streams, records, sealed types)
- Git workflow, semantic commits
- DSA fundamentals: arrays, strings, hashing, recursion

### Phase 2 — Backend
- Spring Boot fundamentals (IoC, DI, auto-config)
- REST API design (status codes, versioning, error handling)
- Persistence (JPA/Hibernate, transactions)
- Testing: JUnit 5, `@SpringBootTest`, slices, Testcontainers

### Phase 3 — Frontend
- TypeScript essentials
- React components, hooks, state management
- API integration & data fetching
- Frontend architecture & testing (Vitest + RTL)

### Phase 4 — Full-Stack
- Connect React ↔ Spring Boot
- CORS, auth flows, DTO contracts
- End-to-end example app

### Phase 5 — System Design
- Fundamentals → distributed systems → scalability
- Databases, caching, messaging
- Microservices & architecture patterns
- Case studies + trade-offs

### Phase 6 — POCs (learn by breaking things)
- Kafka, Redis, databases, distributed systems
- Authentication, caching, concurrency, cloud

### Phase 7 — Depth & Mastery
- Observability, performance tuning, resilience
- Advanced patterns, DDD, event-driven architecture

---

##  Conventions

- **Modules are self-contained.** Each has a README and can be run/tested alone.
- **Commits:** small and focused. Prefer `type(scope): message` (e.g. `feat(dsa): add binary search`).
- **Tests are first-class.** New executable examples ship with tests.
- **Docs answer "why."** Especially in `system-design/` — always include trade-offs.

---

##  Glossary

> Add terms as you encounter them.

| Term | Meaning |
|------|---------|
| BOM  | Bill of Materials — managed dependency versions |
| DTO  | Data Transfer Object |
| IoC  | Inversion of Control |
| ...  | ... |
