# Database Alternatives Analysis for Flock

## Executive Summary

**Current Recommendation (Nifty 200): PostgreSQL Only**

**Future Recommendation (Global Listings): Hybrid Architecture** — PostgreSQL for live API + TimescaleDB for time-series + ClickHouse for analytics + Redis cache.

| Database | Current (Nifty 200) | Future (Global) | Best For |
|----------|---------------------|-----------------|----------|
| **PostgreSQL** | ✅ **Primary DB** | ✅ **Live API** | Point lookups, metadata, SCD2 |
| **ClickHouse** | ❌ Not needed yet | ✅ **Analytics** | Historical aggregations, backtesting |
| **TimescaleDB** | ❌ Not needed yet | ✅ **Tick Data** | Intraday time-series storage |
| **Redis** | ⚠️ Optional | ✅ **Cache** | Hot path caching |
| MySQL | ❌ Not recommended | ❌ Not recommended | No advantage over Postgres |
| MongoDB | ❌ Not recommended | ❌ Not recommended | Document model mismatch |
| DuckDB | ⚠️ Local only | ⚠️ Local only | ETL, analysis (not serving) |

| Database | Verdict | Best For |
|----------|---------|----------|
| **PostgreSQL** | ✅ **Live API** | Point lookups, metadata, SCD2 |
| **ClickHouse** | ✅ **Analytics** | Historical aggregations, backtesting |
| **TimescaleDB** | ✅ **Tick Data** | Intraday time-series storage |
| **Redis** | ✅ **Cache** | Hot path caching |
| MySQL | ❌ Not recommended | No advantage over Postgres |
| MongoDB | ❌ Not recommended | Document model mismatch |
| DuckDB | ⚠️ Local only | ETL, analysis (not serving) |

---

## Current vs Future Requirements

| Requirement | Current (Nifty 200) | Future (All Listings) |
|-------------|---------------------|----------------------|
| **Data Volume** | ~200 stocks | 10,000+ stocks (global) |
| **Historical Data** | ~50K rows | 500M+ rows (daily OHLCV) |
| **Tick Data** | None | 10B+ rows (if stored) |
| **Query Pattern** | Point lookups | Mixed: OLTP + OLAP |
| **Latency** | Sub-second API | Sub-second + analytical |
| **Write Throughput** | Low (daily updates) | High (intrady ticks) |
| **Transactions** | ACID required | ACID + eventual consistency |
| **Schema** | Structured | Structured + time-series |
| **Complexity** | Single container | Distributed architecture |

---

## What You Need RIGHT NOW (Nifty 200)

**PostgreSQL is all you need.** Here's why:

```
Current Scale:
  200 stocks × 250 trading days × 10 years = 500K daily rows
  200 stocks × 50 fundamentals × 40 quarters = 400K fundamental rows
  
  Total: ~1M rows maximum

PostgreSQL Sweet Spot: <100M rows, point lookups
Current Load: ~1% of PostgreSQL capacity
```

**Current Architecture:**
```
┌──────────────┐
│  FastAPI     │
│  (AsyncPG)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  (All data)  │
└──────────────┘
```

**Why PostgreSQL alone works:**
- Sub-millisecond point lookups by ticker
- Handles SCD2 versioning with window functions
- asyncpg provides excellent async Python support
- Single Docker container = simple operations
- ~$40/month on AWS (or free on-prem)
- Room to grow 100x before needing to scale

**When to add more:**
| Add this | When you hit |
|----------|--------------|
| Redis cache | 1M+ rows OR slow queries on hot stocks |
| TimescaleDB | Storing intraday tick data |
| ClickHouse | 100M+ rows OR slow analytical queries |

---

## 1. PostgreSQL (Current)

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (AsyncPG)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  (Relational)│
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **ACID Compliance** | Full transactional integrity for score calculations |
| **JSONB Support** | Store flexible metadata alongside structured data |
| **Async Driver** | `asyncpg` provides excellent async/await support |
| **SCD2 Friendly** | Window functions, CTEs for versioned data |
| **Maturity** | 25+ years, battle-tested in production |
| **Ecosystem** | Rich tooling (pgAdmin, DBeaver, migrations) |
| **Docker** | Simple single-container setup |
| **Cost** | Free, open-source, no licensing |

### Cons
| Category | Details |
|----------|---------|
| **Time-Series** | Not optimized for high-frequency tick data |
| **Analytics** | Slower than columnar DBs for billion-row aggregations |
| **Horizontal Scale** | Sharding requires additional tooling (Citus, Vitess) |
| **Write Throughput** | ~10K writes/sec per node (sufficient for current needs) |

### Best Fit For
- ✅ Live stock API with point lookups
- ✅ SCD2 versioned data (flock_scores, fundamentals)
- ✅ Relational data with foreign keys
- ✅ Metadata storage (tickers, company info, sectors)
- ⚠️ NOT for historical tick data at global scale

### Scaling to Global Listings (Future)

When you expand beyond Nifty 200, PostgreSQL alone will eventually struggle:

```
Scale Calculation:
  10,000 stocks × 250 trading days × 10 years = 25M daily rows
  10,000 stocks × 1,000 ticks/day × 250 days × 10 years = 25B tick rows

PostgreSQL Sweet Spot: <100M rows, point lookups
Beyond This: Hybrid architecture needed
```

See "Recommended Architecture Evolution" section for migration path.

---

## 2. MySQL / MariaDB

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (Aiomysql)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  MySQL 8     │
│  (Relational)│
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **Read Performance** | Slightly faster than Postgres for simple SELECTs |
| **Replication** | Built-in master-slave replication |
| **Familiarity** | Widely known, extensive documentation |
| **Tooling** | MySQL Workbench, phpMyAdmin |

### Cons
| Category | Details |
|----------|---------|
| **JSON Support** | Weaker than Postgres JSONB |
| **Advanced Features** | No window functions in older versions, limited CTEs |
| **SCD2 Complexity** | More verbose queries for versioned data |
| **Async Driver** | `aiomysql` less mature than `asyncpg` |
| **Feature Parity** | Lacks advanced indexing (GIN, GiST) |

### Verdict
**Not recommended** - PostgreSQL strictly better for Flock's use case. MySQL excels at simple web app CRUD, not financial data with SCD2 versioning.

---

## 3. MongoDB

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (Motor)     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  MongoDB     │
│  (Document)  │
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **Schema Flexibility** | Add fields without migrations |
| **Horizontal Scale** | Native sharding, easier than RDBMS |
| **Document Model** | Store nested data (e.g., `{ticker, scores: {...}}`) |
| **Write Throughput** | High write throughput for unstructured data |

### Cons
| Category | Details |
|----------|---------|
| **ACID Transactions** | Limited to single-document (multi-document transactions are slow) |
| **Joins** | No native joins; requires application-level lookups |
| **SCD2 Complexity** | Must manually manage versioning in documents |
| **Query Complexity** | Aggregation pipeline verbose for analytical queries |
| **Data Integrity** | No foreign keys, weaker constraints |
| **Async Driver** | `Motor` is mature but different paradigm |

### Verdict
**Not recommended** - Flock's data is highly structured (stocks, scores, fundamentals) with clear relationships. Document model adds complexity without benefits.

---

## 4. TimescaleDB

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (AsyncPG)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  TimescaleDB │
│  (Postgres   │
│   + Time     │
│   Series)    │
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **PostgreSQL Compatible** | Same SQL, same drivers, same ecosystem |
| **Time-Series Optimized** | Automatic partitioning by time (hypertables) |
| **Compression** | 90%+ compression for time-series data |
| **Continuous Aggregates** | Materialized views that auto-refresh |
| **Time Functions** | `time_bucket()`, gap-filling, interpolation |
| **SCD2 Support** | Still supports standard Postgres features |

### Cons
| Category | Details |
|----------|---------|
| **Complexity** | Additional concepts (hypertables, chunks) |
| **Overhead** | Slight overhead for non-time-series queries |
| **License** | Apache 2.0 (changed from Postgres license in 2021) |
| **Use Case Mismatch** | Optimized for time-series; Flock uses point lookups |

### Best Fit For
- ✅ Intraday tick data (1,000+ ticks/stock/day)
- ✅ Time-range queries ("last 30 days of price history")
- ⚠️ Overkill for current SCD2 fundamentals

### Verdict
**Recommended for tick data** - For global listings with intraday data, TimescaleDB is the optimal choice. Keeps Postgres compatibility while handling time-series at scale.

---

## 5. ClickHouse

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (HTTP/CLI)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  ClickHouse  │
│  (Columnar)  │
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **Analytics Performance** | 100-1000x faster than Postgres for aggregations |
| **Compression** | Columnar storage = excellent compression |
| **Write Throughput** | Millions of rows per second |
| **Time-Series** | Native time-series functions |
| **SQL Dialect** | Standard SQL with analytical extensions |

### Cons
| Category | Details |
|----------|---------|
| **OLTP Workloads** | Terrible at point lookups (row-by-row access) |
| **ACID Transactions** | No transactions; eventual consistency only |
| **SCD2 Support** | Must manually implement versioning |
| **Concurrency** | Limited concurrent query support |
| **Foreign Keys** | No referential integrity |
| **Async Driver** | No mature async Python driver |
| **Operational Complexity** | Requires ZooKeeper for distributed mode |

### Best Fit For
- ✅ Billion-row analytical queries
- ✅ Real-time dashboards with aggregations
- ⚠️ NOT for point lookups by ticker

### Verdict
**Recommended for analytics** - For global listings with backtesting needs, ClickHouse is ideal for analytical queries. Use in hybrid architecture: Postgres for live API, ClickHouse for historical analysis.

---

## 6. DuckDB

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (Embedded)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  DuckDB      │
│  (Embedded   │
│   Columnar)  │
└──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **Embedded** | No server; single-file database |
| **Analytics** | Columnar = fast aggregations |
| **Simplicity** | Zero operational overhead |
| **Parquet Support** | Native Parquet integration |
| **Python Integration** | Pandas/Polars interoperability |

### Cons
| Category | Details |
|----------|---------|
| **Concurrency** | Single-writer only (WAL lock) |
| **Network Access** | No client-server architecture |
| **ACID** | Limited transaction support |
| **SCD2** | No built-in versioning support |
| **Scale** | Not designed for production API backends |

### Best Fit For
- ✅ Local data analysis
- ✅ ETL pipelines
- ⚠️ NOT for production API serving

### Verdict
**Not recommended for production** - DuckDB is perfect for local analytics or ETL, but Flock needs a client-server database for API serving.

---

## 7. Redis

### Architecture
```
┌──────────────┐
│  FastAPI     │
│  (AsyncIO)   │
└──────┬───────┘
       │
       ├─────────────┐
       ▼             ▼
┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │  Redis       │
│  (Primary)   │ │  (Cache)     │
└──────────────┘ └──────────────┘
```

### Pros
| Category | Details |
|----------|---------|
| **Latency** | Sub-millisecond reads |
| **Caching** | Perfect for hot paths (frequently accessed stocks) |
| **Data Structures** | Hashes, sorted sets, streams |
| **Pub/Sub** | Real-time event streaming |
| **Async Driver** | `redis-py` with asyncio support |

### Cons
| Category | Details |
|----------|---------|
| **Persistence** | In-memory (RDB/AOF snapshots, not durable) |
| **Query Language** | Key-value lookups only |
| **SCD2** | No versioning support |
| **Memory Cost** | Expensive for large datasets |
| **Complexity** | Cache invalidation logic |

### Best Fit For
- ✅ Caching layer for hot stocks
- ✅ Real-time price updates (pub/sub)
- ⚠️ NOT as primary database

### Verdict
**Recommended as cache** - Add Redis as a caching layer in front of PostgreSQL for frequently accessed data. Not a replacement for Postgres.

---

## Comparison Matrix

| Feature | PostgreSQL | MySQL | MongoDB | TimescaleDB | ClickHouse | DuckDB | Redis |
|---------|------------|-------|---------|-------------|------------|--------|-------|
| **ACID Transactions** | ✅ Full | ✅ Full | ⚠️ Single-doc | ✅ Full | ❌ None | ⚠️ Limited | ❌ None |
| **SCD2 Support** | ✅ Excellent | ⚠️ Manual | ⚠️ Manual | ✅ Excellent | ❌ Manual | ❌ Manual | ❌ No |
| **Point Lookups** | ✅ Fast | ✅ Fast | ✅ Fast | ✅ Fast | ❌ Slow | ⚠️ Medium | ✅ Instant |
| **Analytics** | ⚠️ Medium | ⚠️ Medium | ⚠️ Medium | ✅ Good | ✅ Excellent | ✅ Excellent | ❌ N/A |
| **Time-Series** | ⚠️ Basic | ⚠️ Basic | ⚠️ Basic | ✅ Excellent | ✅ Excellent | ✅ Good | ⚠️ Streams |
| **Horizontal Scale** | ⚠️ Hard | ✅ Medium | ✅ Easy | ⚠️ Hard | ✅ Medium | ❌ N/A | ✅ Cluster |
| **Async Driver** | ✅ asyncpg | ⚠️ aiomysql | ✅ Motor | ✅ asyncpg | ⚠️ HTTP | ❌ Embedded | ✅ redis-py |
| **Operational Complexity** | ✅ Low | ✅ Low | ⚠️ Medium | ⚠️ Medium | ⚠️ High | ✅ None | ⚠️ Medium |
| **Global Listings Ready** | ⚠️ Phase 1-2 | ❌ No | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Cache only |

---

## Decision Framework

### PostgreSQL (Primary DB)
- ✅ Metadata: ticker, company name, sector, ISIN
- ✅ Live API: point lookups by ticker
- ✅ SCD2 versioned data: flock_scores, fundamentals
- ✅ Reference data: exchanges, currencies, indicators
- ✅ Transactional data: user portfolios, watchlists

### TimescaleDB (Time-Series)
- ✅ Intraday tick data (1,000+ ticks/stock/day)
- ✅ OHLCV candlestick data (1min, 5min, daily)
- ✅ Time-range queries ("last 30 days of price history")
- ✅ Continuous aggregates: rolling averages, volatility
- ✅ Corporate actions history (splits, dividends)

### ClickHouse (Analytics)
- ✅ Historical backtesting (years of data)
- ✅ Cross-sectional analysis ("all stocks with ROE > 15%")
- ✅ Aggregation queries (sector averages, market stats)
- ✅ Materialized views for dashboards
- ✅ Bulk data exports

### Redis (Cache Layer)
- ✅ Hot stocks: top 50 by page views
- ✅ Pre-computed scores: cache Flock score calculations
- ✅ Rate limiting: API throttling per user/IP
- ✅ Session storage: user auth tokens
- ✅ Real-time updates: WebSocket pub/sub for live prices

---

## Recommended Architecture Evolution

### Phase 1: Current (Nifty 200, <1M rows)
```
┌──────────────┐
│  FastAPI     │
│  (AsyncPG)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  (All data)  │
└──────────────┘
```
**Stack**: PostgreSQL 16, asyncpg, Docker

---

### Phase 2: India Expansion (Nifty 500, ~10M rows)
```
┌──────────────┐
│  FastAPI     │
└──────┬───────┘
       ├─────────────┐
       ▼             ▼
┌──────────────┐ ┌──────────────┐
│  Redis       │ │  PostgreSQL  │
│  (Cache)     │ │  (Primary)   │
└──────────────┘ └──────────────┘
```
**Add**: Redis cache for hot stocks, materialized views for sector stats

---

### Phase 3: Global Listings (10,000+ stocks, 100M+ rows)
```
┌──────────────┐
│  FastAPI     │
└──────┬───────┘
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │  TimescaleDB │ │  Redis       │
│  (Metadata)  │ │  (OHLCV)     │ │  (Cache)     │
└──────────────┘ └──────────────┘ └──────────────┘
       │
       │ CDC (Debezium)
       ▼
┌──────────────┐
│  ClickHouse  │
│  (Analytics) │
└──────────────┘
```
**Add**: TimescaleDB for time-series, ClickHouse for backtesting, CDC pipeline

---

### Phase 4: Full Scale (50,000+ stocks, 1B+ rows)
```
┌─────────────────────────────────────────────────────────┐
│  API Layer: FastAPI + Kong/APISIX Gateway               │
└─────────────────────────────────────────────────────────┘
       │
       ├─────────────┬─────────────┬─────────────┐
       ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │  TimescaleDB │ │  ClickHouse  │ │  Redis       │
│  Cluster     │ │  Cluster     │ │  Cluster     │ │  Cluster     │
│  (Citus)     │ │  (Distributed)│ │  (Distributed)│ │  (Cluster)   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │
       │ CDC (Debezium → Kafka)
       ▼
┌─────────────────────────────────────────────────────────┐
│  Data Lake: S3 + Apache Iceberg (historical archive)    │
└─────────────────────────────────────────────────────────┘
```
**Add**: Horizontal scaling, Kafka for event streaming, Iceberg for cold storage

---

## Cost Comparison (Monthly, AWS)

| Database | Compute | Storage | Total/mo |
|----------|---------|---------|----------|
| PostgreSQL (t3.medium) | ~$30 | ~$10 (EBS) | ~$40 |
| MySQL (t3.medium) | ~$30 | ~$10 (EBS) | ~$40 |
| MongoDB Atlas (M10) | ~$60 | ~$20 | ~$80 |
| TimescaleDB (t3.medium) | ~$30 | ~$10 (EBS) | ~$40 |
| ClickHouse (self-hosted) | ~$60 | ~$20 | ~$80 |
| DuckDB | $0 (embedded) | ~$10 (EBS) | ~$10 |
| Redis (cache.t3.micro) | ~$15 | In-memory | ~$15 |

---

## Final Recommendation

### ✅ For Flock's Current Stage (Nifty 200): **PostgreSQL Only**

**Stick with PostgreSQL.** You don't need anything else right now.

**Why:**
1. **Right tool for the job** - Point lookups + SCD2 versioning = relational DB
2. **Async ecosystem** - `asyncpg` is mature and fast
3. **Low complexity** - Single container, easy to operate
4. **ACID compliance** - Critical for financial data integrity
5. **Cost effective** - ~$40/mo on AWS, or free on-prem
6. **Massive headroom** - Current ~1M rows is ~1% of what PostgreSQL handles comfortably

**Architecture:**
```
┌──────────────┐
│  FastAPI     │
│  (AsyncPG)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  (All data)  │
└──────────────┘
```

---

### 📅 For Global Listings (10,000+ stocks): **Hybrid Architecture**

| Component | Database | Purpose |
|-----------|----------|---------|
| **Primary DB** | PostgreSQL | Metadata, live API, SCD2 scores |
| **Time-Series** | TimescaleDB | OHLCV data, intraday ticks |
| **Analytics** | ClickHouse | Backtesting, aggregations |
| **Cache** | Redis | Hot stocks, rate limiting |

**When to Migrate (Current Scale Triggers):**

| You're experiencing... | Add this |
|------------------------|----------|
| Hot stocks loading slowly | Redis cache for top 50 tickers |
| Need intraday tick storage | TimescaleDB hypertables |
| Analytical queries taking seconds | ClickHouse for aggregations |
| Table scans on 10M+ rows | Partitioning or TimescaleDB |

**Rule of thumb:** Stay with PostgreSQL-only until you actually hit performance issues. Premature optimization adds complexity without benefit.

---

### Do NOT Migrate To:
- **MySQL** - No advantage over Postgres for this use case
- **MongoDB** - Document model mismatch for structured financial data
- **DuckDB** - Not designed for production API serving
- **Pure NoSQL** - Financial data needs ACID + relational integrity

---

---

## Current Decision

**Use PostgreSQL only.** Revisit this document when:
- You exceed 1M rows in any single table, OR
- You start storing intraday tick data, OR  
- You expand beyond Nifty 200 to 1,000+ stocks

---

*Document created: 2026-05-01*
*Last updated: 2026-05-01 (clarified current vs. future needs)*
*Review trigger: When stock universe exceeds 1,000 tickers, or any table exceeds 1M rows*
