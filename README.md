#  Software Engineering Atlas

> A long-term **master learning repository** and **hands-on laboratory** for full-stack
> software engineering — backend, frontend, data structures & algorithms, system design,
> and runnable proof-of-concepts (POCs).

This repo is intentionally structured to **grow**. It starts as a clean skeleton with
detailed documentation and evolves into a comprehensive, executable knowledge base.

---

##  Purpose

- Build **deep, durable understanding** across the full stack.
- Keep **runnable, isolated examples** — every concept is something you can execute.
- Document the **why** (trade-offs, complexity, design decisions), not just the how.
- Serve as a **personal reference** you return to for years.

---

##  Repository Structure

Organized **by discipline** for clarity and scalability:

```
software-engineering-atlas/
├── backend/          # Java, Spring Boot, REST, microservices, concurrency, patterns
├── dsa/              # Data structures & algorithms (executable Java + tests)
├── system-design/    # Deep-dive markdown notes: distributed systems, scaling, etc.
├── frontend/         # React + TypeScript, components, state, API integration
├── fullstack/        # End-to-end examples wiring React ↔ Spring Boot
├── pocs/             # Independent, runnable experiments (Kafka, Redis, auth, ...)
├── testing/          # Testing strategy: JUnit 5, Spring tests, Vitest, integration
├── docs/             # Learning roadmap, glossary, conventions
├── pom.xml           # Maven multi-module parent (backend, dsa, pocs)
├── .gitignore
└── README.md         # You are here
```

Each top-level directory has its **own README** explaining its scope, layout, and how to run things.

---

##  Technology Stack

| Layer          | Technology                                             |
|----------------|--------------------------------------------------------|
| Language (BE)  | **Java 21 LTS**                                        |
| Framework      | **Spring Boot 3.3.x**                                  |
| Build (BE)     | **Maven** (multi-module)                               |
| Testing (BE)   | **JUnit 5**, Spring Boot Test, Testcontainers          |
| Language (FE)  | **TypeScript**                                          |
| Framework (FE) | **React 18** + **Vite**                                |
| Testing (FE)   | **Vitest** + **React Testing Library**                 |
| Messaging      | Kafka (POC)                                             |
| Caching        | Redis (POC)                                             |
| Databases      | PostgreSQL / H2 (examples & POCs)                       |

---

##  Getting Started

### Prerequisites
- **JDK 21** (`java -version` → 21.x)
- **Maven 3.9+** (`mvn -v`)
- **Node.js 20+** and **npm** (for frontend)
- **Docker** (optional; needed later for some POCs like Kafka/Redis)

### Build all Java modules
```bash
mvn clean install
```

### Run the frontend (once scaffolded)
```bash
cd frontend/react-app
npm install
npm run dev
```

> ℹ This is currently a **documented skeleton** — directories and READMEs are in place,
> and code samples will be filled in incrementally. Each module's README tracks its status.

---

##  Learning Roadmap

A suggested path (see [`docs/README.md`](docs/README.md) for the full roadmap):

1. **Foundations** → Java core, DSA basics, Git.
2. **Backend** → Spring Boot, REST, persistence, testing.
3. **Frontend** → React + TypeScript, components, state, API integration.
4. **Full-Stack** → Wire it together end-to-end.
5. **System Design** → Scalability, distributed systems, trade-offs.
6. **POCs** → Kafka, Redis, auth, caching, concurrency, cloud.
7. **Depth** → Microservices, observability, performance, patterns.

---

##  Conventions

- **One concept, one runnable unit** where possible.
- Every example ships with a short **README** and, where relevant, **tests**.
- System design notes live as `.md` and always include a **Trade-offs** section.
- Commit early, commit often. Small, focused commits.

---

##  License

Personal learning repository. Add a `LICENSE` file if you intend to share publicly.
