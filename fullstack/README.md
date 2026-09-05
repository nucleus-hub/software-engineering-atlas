# Full-Stack

End-to-end examples that connect the **React + TypeScript** frontend with the
**Spring Boot** backend.

## Goals
- Wire a React app to a Spring Boot REST API
- Handle **CORS** correctly
- Share a clear **DTO / contract** between FE and BE
- Implement an auth flow (login -> token -> protected calls)
- Manage loading/error states end to end
- Run both sides together locally

## Planned structure

```
fullstack/
├── example-app/
│   ├── backend/     # Spring Boot service (may reuse backend/rest-apis patterns)
│   └── frontend/    # React + TS client
└── README.md
```

## Running (planned)
```bash
# terminal 1 - backend
mvn -pl fullstack/example-app/backend -am spring-boot:run
# terminal 2 - frontend
cd fullstack/example-app/frontend && npm install && npm run dev
```

## Status
Skeleton. First end-to-end example lands after backend + frontend basics exist.
