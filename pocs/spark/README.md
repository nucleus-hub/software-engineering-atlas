# POC: Spark

Demonstrates distributed data processing with **Apache Spark** (Java API).

## Goals
- Spin up a local `SparkSession`
- RDD vs DataFrame/Dataset APIs
- Transformations vs actions (lazy evaluation)
- Spark SQL over structured data
- Reading/writing common formats (CSV, JSON, Parquet)
- Understand partitions, shuffles, and the DAG

## Prerequisites
- Spark 3.5.x officially supports Java 8/11/17. If you run into issues on
  Java 21, use a **JDK 17** toolchain for this module specifically.

## Run (planned)
```bash
mvn -pl pocs/spark -am package
# then submit or run a main class locally, e.g.:
mvn -pl pocs/spark -am exec:java -Dexec.mainClass=dev.atlas.spark.WordCount
```

## Status
Skeleton. Add small, self-contained jobs under `src/main/java/dev/atlas/spark`.
