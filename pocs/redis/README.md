# POC: Redis

Demonstrates Redis for caching and beyond.

## Goals
- Basic key/value operations and TTL
- Redis data structures (hashes, lists, sets, sorted sets)
- Cache-aside pattern
- Pub/Sub messaging

## Prerequisites
- Docker (a `docker-compose.yml` for Redis will be added with the code)

## Run (planned)
```bash
docker compose up -d          # start Redis
mvn -pl pocs/redis -am spring-boot:run
```

## Status
Skeleton.
