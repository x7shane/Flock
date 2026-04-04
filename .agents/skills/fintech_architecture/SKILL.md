---
name: fintech_architecture
description: >
  System architecture reference for River — covering database design, event-driven
  systems, microservices patterns, scalability, open-source technology stack, and
  deployment on Linux-based infrastructure. Use when designing or reviewing the
  tech stack, database schema, service topology, or infrastructure layout.
---

# Fintech System Architecture — River's Reference

> **RULE:** Build for correctness first, then performance. A fast system that
> occasionally double-charges users is worthless. Correctness in financial
> systems means ACID guarantees, idempotency, and immutable audit trails — always.

---

## 1. Database Stack

### The Standard Hybrid Architecture

| Layer | Technology | Role | Why |
|---|---|---|---|
| **In-Memory** | Redis 7+ | Real-time price pub/sub, order book cache, session store, rate limiting | Sub-ms latency; native pub/sub; atomic operations |
| **Transactional** | PostgreSQL 16+ | Core financial ledger: balances, orders, settlements, audit trails | ACID compliance; battle-tested; rich SQL; open-source |
| **Time-Series** | TimescaleDB | Historical market data (OHLCV ticks), analytics, charting | PostgreSQL extension; hypertables auto-partition by time |
| **Event Bus** | Apache Kafka | Decouple execution engines from persistence; event replay; audit | Durable; replayable; handles burst traffic |
| **Search** | Elasticsearch | Transaction search, compliance queries, fraud detection | Full-text + structured queries at scale |
| **Cache / Config** | Redis | Feature flags, rate limiting config, distributed locks | Single source of truth for transient shared state |

**All of the above are:**
- ✅ 100% open-source
- ✅ Linux-native (run on Ubuntu Server / Debian LTS)
- ✅ Docker-containerizable
- ✅ Kubernetes-orchestratable
- ✅ Used in production by major financial institutions globally

---

### PostgreSQL — Schema Design Principles

```sql
-- ALWAYS use UUID primary keys (not sequential int — prevents enumeration attacks)
CREATE TABLE accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    balance     NUMERIC(20, 6) NOT NULL DEFAULT 0,  -- Never use FLOAT for money
    currency    CHAR(3) NOT NULL DEFAULT 'INR',
    status      VARCHAR(20) NOT NULL CHECK (status IN ('ACTIVE', 'FROZEN', 'CLOSED')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ledger pattern: APPEND-ONLY (never UPDATE balances directly)
CREATE TABLE ledger_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id),
    amount          NUMERIC(20, 6) NOT NULL,   -- Positive = credit, Negative = debit
    running_balance NUMERIC(20, 6) NOT NULL,
    entry_type      VARCHAR(50) NOT NULL,
    reference_id    UUID NOT NULL,             -- Links to order/payment
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Critical Rules:**
- **NEVER store money as FLOAT.** Use `NUMERIC(20,6)` or `BIGINT` (paise/smallest unit).
- **Never UPDATE balances directly.** Use a double-entry ledger — every debit has a matching credit.
- **Use database transactions for all fund movements.** If any step fails, the entire transaction rolls back.
- **Optimistic Locking:** Use `version` column + check in WHERE clause to prevent race conditions on balance updates.

---

### TimescaleDB — Tick Data Schema

```sql
-- TimescaleDB hypertable for market data
CREATE TABLE market_ticks (
    time        TIMESTAMPTZ NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    exchange    VARCHAR(10) NOT NULL,
    ltp         NUMERIC(12, 4),
    volume      BIGINT,
    open        NUMERIC(12, 4),
    high        NUMERIC(12, 4),
    low         NUMERIC(12, 4),
    close       NUMERIC(12, 4)
);

-- Convert to hypertable (partitions by time automatically)
SELECT create_hypertable('market_ticks', 'time');

-- Continuous aggregate for OHLCV candles (auto-refreshed)
CREATE MATERIALIZED VIEW ohlcv_1min
WITH (timescaledb.continuous) AS
SELECT symbol,
       time_bucket('1 minute', time) AS bucket,
       FIRST(ltp, time) AS open,
       MAX(ltp) AS high,
       MIN(ltp) AS low,
       LAST(ltp, time) AS close,
       SUM(volume) AS volume
FROM market_ticks
GROUP BY symbol, bucket;
```

---

## 2. Microservices Architecture

### Service Topology for a Trading/Fintech Platform

```
┌─────────────────────────────────────────────────┐
│                  API Gateway                     │
│      (Auth + Rate Limiting + Routing)            │
└──────┬──────────┬──────────┬────────────────────┘
       │          │          │
  ┌────▼───┐ ┌───▼────┐ ┌───▼──────┐
  │ User   │ │ Order  │ │ Market   │
  │ Svc    │ │ Engine │ │ Data Svc │
  └────┬───┘ └───┬────┘ └───┬──────┘
       │         │           │
  ┌────▼─────────▼───────────▼──────┐
  │           Kafka Event Bus        │
  └────┬──────────┬─────────┬───────┘
       │          │         │
  ┌────▼───┐ ┌───▼────┐ ┌───▼──────┐
  │Ledger  │ │Notif.  │ │Analytics │
  │Svc     │ │Svc     │ │Svc       │
  └────┬───┘ └────────┘ └────┬─────┘
       │                     │
  ┌────▼──────┐        ┌─────▼──────┐
  │PostgreSQL │        │TimescaleDB │
  └───────────┘        └────────────┘
```

### Service Communication Rules
| Pattern | When to Use |
|---|---|
| **Synchronous REST** | User-facing requests requiring immediate response (auth, portfolio view) |
| **Synchronous gRPC** | Internal service calls where latency matters (order engine ↔ risk engine) |
| **Async Kafka Events** | When sender doesn't need immediate confirmation (audit logging, notifications, analytics) |
| **Never:** Direct DB access from another service | Each service owns its own data store; data sharing via events only |

---

## 3. Event-Driven Design Patterns

### Outbox Pattern (Critical for Financial Systems)
```
Problem: What if we update the DB but fail to publish the Kafka event?
Solution: Write to DB AND outbox table in same transaction.
          A separate "outbox relay" service publishes events from outbox to Kafka.

CREATE TABLE outbox_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type  VARCHAR(100) NOT NULL,
    payload     JSONB NOT NULL,
    published   BOOLEAN DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Outbox relay reads unpublished events and publishes to Kafka, then marks published=true
```

### Idempotency Pattern (Critical for Payments)
```python
# Every payment handler must be idempotent
def process_payment(idempotency_key: str, amount: float, ...) -> dict:
    # Check if already processed
    cached = redis.get(f"payment:{idempotency_key}")
    if cached:
        return json.loads(cached)  # Return same result as first call

    # Process payment
    result = execute_payment(amount, ...)

    # Cache result for 24 hours
    redis.setex(f"payment:{idempotency_key}", 86400, json.dumps(result))
    return result
```

---

## 4. Infrastructure & Deployment

### Linux Server Configuration (Security Hardened)
```bash
# OS: Ubuntu Server 24.04 LTS

# Essential hardening
ufw enable                          # Firewall enabled
ufw default deny incoming           # Block all inbound by default
ufw allow 22/tcp                    # SSH (restrict further by IP)
ufw allow 443/tcp                   # HTTPS only

# Disable root login, use key-based auth only
# /etc/ssh/sshd_config:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# Automatic security updates
apt install unattended-upgrades
```

### Container & Orchestration Stack
| Tool | Role |
|---|---|
| **Docker** | Containerize each service with minimal base images (Alpine or Distroless) |
| **Kubernetes (K8s)** | Orchestrate, auto-scale, self-heal containers |
| **Helm** | Package and manage K8s deployments |
| **Istio** | Service mesh — mTLS between services, traffic management, observability |
| **Prometheus + Grafana** | Metrics collection and dashboarding |
| **Loki** | Log aggregation (Grafana-native) |
| **Jaeger / Tempo** | Distributed tracing across microservices |

---

## 5. Scalability Patterns

### Database Scaling Strategy
```
Read-heavy (analytics, charting):
  → Read replicas for TimescaleDB and PostgreSQL
  → Query analytics data NEVER from the primary transactional DB

Write-heavy (order ingestion, tick data):
  → Kafka as write buffer → async batch insert to TimescaleDB
  → PostgreSQL connection pooling via PgBouncer (pool_mode=transaction)

Extreme scale (millions of users):
  → Citus extension for distributed PostgreSQL
  → Partition user accounts table by user_id hash
```

### Caching Strategy (Redis)
```
L1 Cache (in-process, < 1ms):  Local Python dict, expire after 1 second
L2 Cache (Redis, < 5ms):       Market data, user portfolio snapshots
L3 Cache (PostgreSQL, < 50ms): Historical and analytical queries

Cache invalidation:
  - Time-based TTL for market data (5 seconds for tick data)
  - Event-driven invalidation for user-specific data (balance updates)
  - Never cache sensitive financial values without encryption
```

---

## 6. Open-Source Stack Summary (Linux-Native)

| Category | Tool | License |
|---|---|---|
| OS | Ubuntu Server LTS / Debian | GPL |
| Database | PostgreSQL | PostgreSQL License (free) |
| Time-Series | TimescaleDB (Community) | Apache 2.0 |
| Cache | Redis 7 | BSD 3-Clause |
| Event Bus | Apache Kafka | Apache 2.0 |
| Search | Elasticsearch (BSL, free for internal) | BSL 1.1 |
| Container | Docker | Apache 2.0 |
| Orchestration | Kubernetes | Apache 2.0 |
| Service Mesh | Istio | Apache 2.0 |
| Secret Mgmt | HashiCorp Vault | BSL 1.1 (free for single cluster) |
| Monitoring | Prometheus + Grafana | Apache 2.0 |
| CI/CD | GitHub Actions / GitLab CI | Free tier |
| API Gateway | Kong / Traefik | Apache 2.0 |
