# REST APIs

Designing and building RESTful APIs with Spring Boot.

## Topics
- Resource modeling and URI design
- HTTP methods, status codes, idempotency
- Request validation (`jakarta.validation`)
- Centralized error handling (`@ControllerAdvice`)
- Pagination, filtering, sorting
- API versioning strategies
- OpenAPI/Swagger documentation

## Run / Test
```bash
mvn -pl backend/rest-apis -am spring-boot:run   # once an app class exists
mvn -pl backend/rest-apis -am test
```

## Status
Skeleton. Add controllers, DTOs, and MockMvc/WebTestClient tests.
