# Apache Iceberg Use Case Analysis for Flock

## Executive Summary

Apache Iceberg is **not recommended** for Flock's current scale, but documents potential future use cases as the platform scales to petabyte-level analytics workloads.

---

## Current Architecture (PostgreSQL)

| Characteristic | Current State |
|---------------|---------------|
| **Data Volume** | ~200 stocks (Nifty 200) |
| **Storage** | PostgreSQL 16 |
| **Query Pattern** | Point lookups by ticker, SCD2 versioning |
| **Latency** | Sub-second API responses |
| **Infrastructure** | Single Docker container |

---

## When to Consider Apache Iceberg

### 1. Historical Tick Data Warehouse

**Trigger**: Storing intraday tick data for backtesting

```
Scale: 200 stocks × 1,000 ticks/day × 250 trading days × 10 years
       = 500 billion+ rows

Current: PostgreSQL would struggle with billion-row tables
Iceberg: Native partitioning, efficient pruning, petabyte-scale
```

**Architecture**:
```
┌─────────────────┐     ┌──────────────────┐
│ PostgreSQL      │────▶│ Iceberg (S3)     │
│ (Live API)      │ CDC │ (Historical)     │
└─────────────────┘     └──────────────────┘
```

---

### 2. ML Feature Store

**Trigger**: Training ML models on years of fundamental + price history

| Requirement | Iceberg Benefit |
|------------|-----------------|
| Time-travel queries | Snapshot isolation for reproducible training sets |
| Schema evolution | Add features without breaking pipelines |
| ACID transactions | Safe concurrent feature engineering |
| Partition evolution | Reorganize data as query patterns change |

**Example**:
```sql
-- Time-travel to get training set as of 2024-01-01
SELECT * FROM features FOR SYSTEM_TIME AS OF '2024-01-01'
WHERE snapshot_id = '...'
```

---

### 3. Multi-Petabyte Data Lake

**Trigger**: Multiple teams sharing a unified data platform

```
Teams:       Data Engineering, Quant Research, Risk, Analytics
Sources:     NSE, BSE, Reuters, Bloomberg, Alternative data
Formats:     Parquet, JSON, Avro, ORC
Queries:     Spark, Trino, Presto, Athena, DuckDB
```

Iceberg provides:
- **Unified table format** across all engines
- **Hidden partitioning** - no manual partition management
- **Schema evolution** without data migration

---

### 4. Regulatory Audit Trail

**Trigger**: SEBI compliance requiring historical data retention

| Requirement | Iceberg Feature |
|------------|-----------------|
| 7-year retention | Time-travel to any historical snapshot |
| Audit queries | `SELECT ... FOR SYSTEM_TIME AS OF` |
| Data lineage | Snapshot metadata tracks all changes |
| Immutable history | Append-only with versioned snapshots |

---

## Infrastructure Requirements for Iceberg

### Minimum Viable Setup

```yaml
# docker-compose.iceberg.yml
services:
  minio:           # S3-compatible object storage
  spark:           # Compute engine for writes
  trino:           # SQL query engine
  rest-catalog:    # Table metadata service
  postgres:        # Still needed for live API
```

### Cloud Architecture

```
┌─────────────────────────────────────────────────────┐
│  AWS                                                │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │  Glue       │  │  S3         │                  │
│  │  Catalog    │  │  (Data)     │                  │
│  └─────────────┘  └─────────────┘                  │
│         ▲                ▲                          │
│  ┌──────┴────────────────┴──────┐                  │
│  │  Spark EMR / Trino Athena    │                  │
│  └──────────────────────────────┘                  │
└─────────────────────────────────────────────────────┘
```

---

## Migration Path (If Needed)

### Phase 1: Hybrid (Now → 10M rows)
- Keep PostgreSQL for live API
- Add Iceberg for historical analytics
- CDC sync from Postgres → Iceberg

### Phase 2: Iceberg-Native (10M → 1B rows)
- Batch writes to Iceberg
- Trino/Spark for analytical queries
- PostgreSQL for low-latency point lookups

### Phase 3: Full Lakehouse (1B+ rows)
- Iceberg as single source of truth
- Materialized views for hot paths
- Delta caching layer for sub-second reads

---

## Cost Comparison

| Component | PostgreSQL | Iceberg (AWS) |
|-----------|------------|---------------|
| Storage | ~$10/mo (EBS) | ~$23/TB/mo (S3) |
| Compute | Included | Spark EMR (~$0.50/hr) |
| Query | Free | Athena (~$5/TB scanned) |
| Complexity | Low | High |

**Verdict**: Iceberg costs 5-10× more for Flock's current scale.

---

## Decision Framework

| Question | If Yes → Consider Iceberg |
|----------|---------------------------|
| Data volume > 100M rows? | ✅ |
| Need time-travel queries? | ✅ |
| Multiple query engines? | ✅ |
| Schema evolution required? | ✅ |
| Petabyte-scale analytics? | ✅ |

**Current Flock**: 0/5 → **PostgreSQL is correct**

---

## References

- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [Iceberg vs Delta Lake vs Hudi](https://lakefs.io/blog/data-lake-format-comparison/)
- [AWS Lake House Architecture](https://aws.amazon.com/big-data/datalakes-and-analytics/lake-house/)

---

*Document created: 2026-05-01*
*Review trigger: When stock universe exceeds 1,000 tickers or historical data exceeds 100M rows*
