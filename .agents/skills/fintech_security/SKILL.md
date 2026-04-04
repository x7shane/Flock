---
name: fintech_security
description: >
  Security architecture reference for River — covering authentication, encryption,
  network security, API hardening, OWASP mitigations, audit trail design, and
  India-specific regulatory security requirements (RBI, DPDP Act).
---

# Fintech Security — River's Reference

> **RULE:** Security is not a phase — it is a property of the system.
> Any feature that moves money or stores personal data must pass a security review
> against this document before it ships.

---

## 1. Authentication & Authorization

### OAuth 2.0 + JWT
- Use **Authorization Code + PKCE** flow for mobile/SPA apps.
- Access tokens expire in **≤ 15 minutes** for financial operations.
- Refresh tokens expire in **24 hours** (stored server-side in Redis, revocable).
- Never store tokens in `localStorage`. Use `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
- Use **RS256** (asymmetric) for JWT signing — backend services verify without sharing a secret.
- Always validate JWT claims: `exp`, `iat`, `iss`, `aud`.
- Maintain a **token revocation list** in Redis for logout and suspicious activity responses.

### Multi-Factor Authentication (MFA)
| Scenario | MFA Type |
|---|---|
| Login from new device | TOTP (Google Authenticator / Authy) |
| Fund transfer / withdrawal | TOTP OR SMS OTP |
| API key generation | TOTP mandatory |
| Password change | Email OTP + TOTP + re-authentication |

---

## 2. Encryption

### Data in Transit
- **TLS 1.3** for all external traffic. Disable TLS 1.0, 1.1, 1.2 entirely.
- **mTLS (Mutual TLS)** for inter-microservice communication.
- **HSTS:** `max-age=31536000; includeSubDomains` on all HTTP responses.
- **Certificate pinning** in mobile apps to prevent MITM attacks.

### Data at Rest — Envelope Encryption
```
1. Generate a Data Encryption Key (DEK) per user/record
2. Encrypt sensitive data with DEK using AES-256-GCM
3. Encrypt DEK with Key Encryption Key (KEK) stored in HSM/KMS
4. Store [encrypted data + encrypted DEK] — KEK never leaves HSM
```

### What to Encrypt (Always)
| Field | Storage Rule |
|---|---|
| Aadhaar Number | Tokenize via UIDAI — never store raw Aadhaar |
| PAN Number | Encrypt, display only last 4 chars |
| Bank Account Number | Encrypt + tokenize |
| UPI PIN | NEVER stored — lives only inside bank HSM |
| Card Number | PCI-DSS: Tokenize — never store raw PAN |
| Password | Argon2id or Bcrypt (cost=12) — never MD5/SHA-1 |

### Hardware Security Modules (HSM)
- Required for: root key storage, UPI PIN crypto, financial transaction signing.
- Options: AWS CloudHSM, AWS KMS, HashiCorp Vault, on-premise Thales HSM.
- **Rule:** Private keys NEVER leave HSM in plaintext. All signing happens inside.

---

## 3. Network Architecture (Defence in Depth)

```
Internet → [WAF + DDoS Protection] → [Load Balancer] (public subnet)
         → [API Gateway] (rate limiting, auth validation, logging)
         → [Application Servers] (private subnet)
         → [Databases + Redis] (isolated private subnet)
         → [HSM / KMS] (separate isolated subnet)
```

### Firewall Rules
- DB servers: Accept ONLY from App server security group on relevant port.
- Redis: Accept ONLY from App server security group.
- App servers: Accept ONLY from Load Balancer on port 443.
- All others: DENY by default.

### API Rate Limiting (Redis Token Bucket)
```
Standard API calls:    100 req/min per user
Payment initiation:    5 req/min per user
Login attempts:        5 attempts / 15 min → account lockout
OTP verification:      3 attempts per OTP → invalidate on 4th
```

---

## 4. OWASP Top 10 — Fintech Mitigations

| Risk | Mitigation |
|---|---|
| Broken Access Control | Server-side RBAC. Never trust client-side auth. |
| Cryptographic Failures | AES-256-GCM at rest. TLS 1.3 in transit. No MD5/SHA-1. |
| Injection | Parameterized queries / ORM always. Never string-concatenate SQL. |
| Insecure Design | STRIDE threat modeling at design phase. |
| Security Misconfiguration | No default passwords. Remove debug endpoints in prod. |
| Vulnerable Components | Snyk + pip-audit + npm audit in CI/CD pipeline. |
| Auth & Session Failures | MFA everywhere. Short-lived JWTs. Account lockout policy. |
| Data Integrity Failures | Sign JWTs. Validate webhook HMAC signatures. |
| Security Logging Failures | Log all auth/payment/admin events. Alert on anomalies < 5 min. |
| SSRF | Whitelist external URLs. Block cloud metadata endpoints (169.254.169.254). |

---

## 5. Financial Operation Controls

- **4-Eyes Principle:** High-value operations (bulk payouts, config changes) require two authorized approvals.
- **Idempotency Keys:** Every payment endpoint must accept `Idempotency-Key` header — prevent duplicate charges.
- **Fat Finger Protection:** Reject payments > 3× user's 30-day average — flag for review.
- **Velocity Checks:** Alert if same user initiates > 10 transactions in < 10 minutes.

---

## 6. Immutable Audit Log (Regulatory Requirement)

Every financial event MUST log:
```json
{
  "event_id": "uuid-v4",
  "event_type": "PAYMENT_INITIATED",
  "timestamp": "ISO-8601",
  "user_id": "u_abc123",
  "ip_address": "masked",
  "amount": 50000,
  "currency": "INR",
  "status": "PENDING"
}
```
- **Append-only** — never UPDATE or DELETE audit records.
- Replicate to at least 2 geographically separate locations.
- **Retain for minimum 5 years** (RBI mandate).

---

## 7. Incident Response Timelines (India Regulatory)

| Phase | Action | Timeline |
|---|---|---|
| Detection | SIEM alert triggers | < 5 minutes |
| Contain | Isolate systems, revoke credentials | < 1 hour |
| Notify RBI | For significant cyber incidents | **Within 6 hours** |
| Notify Users | If personal data compromised | Within 72 hours (DPDP) |
| Eradicate & Recover | Patch, rotate secrets, restore | < 48 hours |
| Post-Mortem | Root cause + runbook update | Within 1 week |

---

## 8. Secrets Management Rules

```
NEVER hardcode credentials. NEVER commit secrets to Git.

Use:
- HashiCorp Vault (self-hosted) OR AWS Secrets Manager
- Environment variables injected at runtime by CI/CD

Rotation Policy:
- API Keys:         Every 90 days
- DB Passwords:     Every 30 days
- TLS Certs:        Auto-renew at 60 days (Let's Encrypt)
- JWT Signing Keys: Every 30 days (support graceful key rollover)
```

---

## 9. Security Testing Checklist (Pre-Launch)

| Test | Tool | Frequency |
|---|---|---|
| SAST | SonarQube, Bandit (Python), Semgrep | Every PR |
| DAST | OWASP ZAP, Burp Suite | Every release |
| Dependency Scan | Snyk, pip-audit, npm audit | Daily (automated) |
| Penetration Testing | External security firm | Pre-launch + annually |
| Infrastructure Scan | Prowler (AWS), Checkov (Terraform) | Weekly |
