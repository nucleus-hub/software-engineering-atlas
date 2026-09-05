# POC: Caching

Demonstrates the Spring Cache abstraction and common caching patterns.

## Goals
- `@Cacheable`, `@CachePut`, `@CacheEvict`
- Cache-aside vs read-through vs write-through
- Eviction policies and TTL
- Measuring cache hit/miss impact
- Pluggable providers (Caffeine locally, Redis via the redis POC)

## Run (planned)
```bash
mvn -pl pocs/caching -am spring-boot:run
```

## Status
Skeleton.
