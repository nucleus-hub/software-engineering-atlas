# POC: Kafka

Demonstrates event streaming with Apache Kafka and Spring Kafka.

## Goals
- Produce and consume messages
- Understand topics, partitions, and consumer groups
- Explore delivery semantics (at-most-once, at-least-once, exactly-once)
- Observe rebalancing and offset management

## Prerequisites
- Docker (a `docker-compose.yml` for Kafka will be added with the code)

## Run (planned)
```bash
docker compose up -d          # start Kafka
mvn -pl pocs/kafka -am spring-boot:run
```

## Status
Skeleton.
