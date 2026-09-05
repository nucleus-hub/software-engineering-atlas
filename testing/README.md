# Testing

A cross-cutting home for the repository's **testing strategy** and shared conventions.
(Most tests live next to the code they cover, in each module's `src/test`.)

## Backend (Java)
- **JUnit 5** (Jupiter) as the test engine
- **Spring Boot Test** — `@SpringBootTest`, slice tests (`@WebMvcTest`, `@DataJpaTest`)
- **MockMvc / WebTestClient** for controllers
- **Mockito** for mocking collaborators
- **Testcontainers** for realistic integration tests (Postgres, Kafka, Redis)
- **AssertJ** for fluent assertions

Run all backend tests:
```bash
mvn test
```

## Frontend (React + TS)
- **Vitest** as the test runner
- **React Testing Library** for component behavior
- **@testing-library/jest-dom** for DOM matchers
- (Optional later) **Playwright** for E2E

Run frontend tests:
```bash
cd frontend/react-app && npm test
```

## Testing pyramid
- **Many** fast unit tests
- **Some** integration tests (slices, Testcontainers)
- **Few** end-to-end tests

## Conventions
- Test names describe behavior: `methodUnderTest_condition_expectedResult`
- Arrange / Act / Assert structure
- Cover edge cases explicitly
- Keep tests deterministic and isolated

## Status
Documentation. Concrete example tests accompany each code module as it grows.
