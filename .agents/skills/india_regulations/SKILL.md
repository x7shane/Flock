---
name: india_regulations
description: >
  Deep knowledge on Indian financial regulations: SEBI, RBI, FEMA, NPCI, KYC/AML,
  UPI architecture, payment aggregator licensing, neobanking rules, digital lending,
  and data protection laws (DPDP Act). For use by River when designing products or
  evaluating legal exposure.
---

# India Financial Regulations — River's Reference

> **RULE:** If any product feature involves user money, identity, or banking data —
> consult this file BEFORE writing a single line of code. Never assume something is
> legal. When in doubt, flag it for legal counsel.

---

## 1. Regulatory Bodies & Their Jurisdiction

| Body | Full Name | Governs |
|---|---|---|
| **SEBI** | Securities and Exchange Board of India | Stock exchanges (NSE/BSE), brokers, mutual funds, listed companies, F&O, algo trading |
| **RBI** | Reserve Bank of India | Banks, NBFCs, payment systems, forex, digital lending, neobanks |
| **NPCI** | National Payments Corporation of India | UPI, IMPS, RuPay, NACH, AePS, BBPS, FASTag |
| **IRDAI** | Insurance Regulatory and Development Authority | Insurance products |
| **PFRDA** | Pension Fund Regulatory and Development Authority | NPS, pension products |
| **FIU-IND** | Financial Intelligence Unit — India | Suspicious transaction reporting (AML) |
| **UIDAI** | Unique Identification Authority of India | Aadhaar-based identity, eKYC |

---

## 2. Stock Market Structure (SEBI-Regulated)

### Exchanges & Key Indices
- **NSE (National Stock Exchange):** Highest trading volume, dominant in F&O. Flagship index: **Nifty 50**.
- **BSE (Bombay Stock Exchange):** Oldest in Asia. Flagship index: **Sensex** (30 stocks). More listed companies, but lower derivatives volume.
- **NSDL / CDSL:** National depositories that hold Demat accounts electronically.
- T+1 settlement: Equity trades settle the next trading day.

### SEBI F&O Reforms (2024–2025) — Critical for Product Design
> These reforms reshaped the retail derivatives landscape. Building an F&O tool or analytics platform must account for ALL of these:

| Reform | Detail | Product Impact |
|---|---|---|
| **Contract Size Increase** | Index derivatives minimum contract value raised to ₹15–20 lakh | Margin calculators must reflect new lot sizes |
| **Weekly Expiry Limit** | Each exchange can offer weekly expiry for only ONE benchmark index | Bank Nifty weekly gone from NSE; reduces "expiry day" event frequency |
| **Upfront Premium** | Option buyers must pay full premium at order time | No intraday premium-based leverage tricks |
| **Expiry Day ELM** | +2% Extreme Loss Margin on short options on expiry day | Risk engines must apply this dynamically |
| **Intraday Monitoring** | Random position limit checks by exchanges throughout the day | Platforms must enforce limits in real-time, not just at EOD |
| **F&O Eligibility Tightening** | Stocks need higher market cap + median quarter-sigma order size ≥ ₹75 lakh | Fewer scrips in F&O; product DB must stay updated |

### SEBI Algo Trading Rules
- All algorithms must be **registered with the broker** before live deployment.
- Strategies must have **complete audit logs** (order ID, timestamp, price, rationale).
- Retail algo traders must use **broker-approved API gateways** (e.g., Kite Connect, SmartAPI).
- DMA (Direct Market Access) only available to institutional investors.

---

## 3. Payment Regulation (RBI)

### Payment Aggregator (PA) Licensing
> **Required if:** Your platform collects money from customers, pools it, and settles with merchants.

| Requirement | Detail |
|---|---|
| **License** | RBI authorization under Payment and Settlement Systems Act, 2007 |
| **Net Worth at Application** | Minimum ₹15 crore |
| **Net Worth by Year 3** | Minimum ₹25 crore |
| **Escrow Account** | Funds must be held in escrow with a scheduled commercial bank. Cannot use for operational expenses. |
| **Data Localization** | ALL payment data of Indian users must be stored ONLY in India |
| **Timeline** | 12–24 months to obtain authorization |
| **KYC/AML** | Full compliance mandatory — no workaround |

### Payment Gateway (PG) vs Payment Aggregator (PA)
- **PA:** Handles funds — REQUIRES RBI license.
- **PG:** Technology layer only, does not touch funds — does NOT require RBI license, but must partner with an authorized PA or bank.

> **For MVP:** Partner with an existing licensed PA (Razorpay, Cashfree, PayU) rather than applying for your own license. Saves 12–24 months.

### UPI Architecture (Technical Deep Dive)

**Participants:**
```
User App (PSP/TPAP) → NPCI Switch (central router) → Remitter Bank → Beneficiary Bank
```

**Key Concepts:**
- **VPA (Virtual Payment Address):** e.g., `user@ybl`. Masks actual bank account. Resolves via NPCI Mapper.
- **PSP:** App operator (Google Pay, PhonePe, bank apps).
- **TPAP (Third-Party App Provider):** Non-bank app (Google Pay, WhatsApp Pay) — needs a **sponsor bank** to connect to NPCI.

**Security in UPI:**
- UPI PIN is NEVER sent in plaintext.
- PIN is hashed (SHA-256 + device-specific salt) → encrypted with bank's RSA public key → transmitted.
- Decrypted only inside bank's **HSM (Hardware Security Module)**.
- All API calls signed with HMAC-SHA256 over TLS 1.2+.

**Idempotency is critical:** UPI callbacks are asynchronous. Always design payment handlers to be **idempotent** — duplicate callbacks must not result in double credits.

**UPI Transaction Limits (2025):**
| Transaction Type | Limit |
|---|---|
| P2P (Person to Person) | ₹1 lakh per transaction |
| P2PM (Person to Merchant, select categories) | ₹2 lakh per transaction |
| UPI Lite (offline/low-balance) | ₹500 per transaction, ₹2,000 wallet limit |

---

## 4. Neobanking & Digital Lending

### Neobanking
- **No standalone neobank license exists in India.** RBI has not issued one.
- Must operate via a **Banking-as-a-Service (BaaS)** model — partner with a licensed scheduled commercial bank or NBFC.
- The neobank acts as a **Technology Service Provider (TSP)** — cannot hold customer deposits independently.
- **Risk:** If partner bank faces RBI action (e.g., Paytm Payments Bank, 2024), your operations are instantly disrupted.
- **Mitigation:** Never rely on a single banking partner. Build multi-bank redundancy from day one.

### Digital Lending (RBI Digital Lending Guidelines, 2022)
| Rule | Detail |
|---|---|
| **Regulated Entity (RE) Mandatory** | Cannot disburse loans without NBFC/bank license. Fintechs act as Lending Service Providers (LSPs). |
| **Loan Sanction Letter** | Must be issued BEFORE any disbursal |
| **APR Disclosure** | Annual Percentage Rate must be clearly disclosed upfront |
| **No Third-Party Data** | Cannot access contacts, media gallery, or location without explicit consent. |
| **Cooling-Off Period** | Borrowers must be given a window to exit the loan without penalty |
| **Data to RE Only** | Borrower data can only be shared with the regulated entity — not third-party marketers |

---

## 5. KYC & AML (India-Specific)

### KYC Hierarchy in India

| KYC Type | Method | Use Case | Authority |
|---|---|---|---|
| **Aadhaar OTP eKYC** | UIDAI API — OTP to Aadhaar-linked mobile | Fastest onboarding | UIDAI (need AUA/KUA license) |
| **Aadhaar Offline eKYC** | XML download with share code | No biometric, user-controlled | UIDAI |
| **Video KYC (V-CIP)** | Live video call with trained officer | Full remote KYC | RBI-mandated for face-to-face equivalent |
| **CKYC** | CERSAI registry lookup via CKYC number | Avoid re-KYC for customers already KYC'd | CERSAI |
| **PAN Verification** | NSDL/UTIITSL PAN API | Tax compliance, identity supplement | Income Tax Dept. |
| **DigiLocker** | Government document vault API | Fetch Aadhaar, PAN, driving license, RC | MeitY |

### KYC Risk Levels
- **Simplified KYC:** Low-risk customers. Basic name, DOB, address.
- **CDD (Customer Due Diligence):** Standard. Verify identity documents, assess risk profile.
- **EDD (Enhanced Due Diligence):** Mandatory for PEPs (Politically Exposed Persons), high-value accounts, and unusual transaction profiles. Ongoing monitoring required.

### AML Obligations

| Obligation | Detail |
|---|---|
| **Transaction Monitoring** | Flag structuring (transactions just below ₹50,000 to avoid reporting), sudden large credits, dormant account reactivation |
| **PEP / Sanctions Screening** | Screen against UN Sanctions List, OFAC, RBI caution list, designated terrorist lists |
| **STR (Suspicious Transaction Report)** | File with FIU-IND within **7 working days** of suspicion |
| **CTR (Cash Transaction Report)** | Cash transactions ≥ ₹10 lakh must be reported to FIU-IND monthly |
| **Record Retention** | Minimum **5 years** for all KYC records and transaction logs |
| **Ongoing Monitoring** | Re-verify KYC periodically (even for existing customers) based on risk category |

---

## 6. Forex in India — FEMA Rules

### Legal Framework
- Governed by **FEMA (Foreign Exchange Management Act), 1999** + RBI circulars.
- Retail forex participation is ONLY legal through **SEBI-registered brokers** on recognized Indian exchanges.

### What is LEGAL
| Instrument | Exchange | Details |
|---|---|---|
| Currency Futures (USD/INR, EUR/INR, GBP/INR, JPY/INR) | NSE / BSE / MSE | Contract value standardized; hedge exposure required |
| Currency Options (same pairs) | NSE / BSE | European-style options only |
| Cross-Currency Futures (EUR/USD, GBP/USD, USD/JPY) | NSE | Available without mandatory underlying exposure |

### What is STRICTLY ILLEGAL for Indian Residents
| Instrument | Reason | Penalty |
|---|---|---|
| Offshore spot forex (e.g., FOREX.com, IC Markets) | Not on Indian exchange, not SEBI-regulated | FEMA: Up to **3× the amount involved** + potential imprisonment |
| CFDs (Contracts for Difference) | Not a permitted instrument under FEMA | Same |
| Binary options | Banned globally; not permitted under FEMA | Same |
| Using LRS funds for speculative forex | LRS is for investment/education, not speculation | FEMA + Income Tax scrutiny |

> ⚠️ **NEVER** build a product that routes Indian users to offshore forex platforms. This is a serious regulatory crime.

---

## 7. Data Protection — DPDP Act (2023)

India's **Digital Personal Data Protection Act (2023)** applies to any entity processing personal data of Indian residents.

| Requirement | Detail |
|---|---|
| **Consent** | Explicit, informed consent required before processing any personal data |
| **Data Minimization** | Collect only what is strictly necessary |
| **Right to Erasure** | Users can request deletion of their data (exceptions for regulated financial records) |
| **Data Fiduciary** | Any entity processing data is a Data Fiduciary — must register if processing large-scale data |
| **Data Protection Officer (DPO)** | Significant Data Fiduciaries must appoint a DPO |
| **Breach Notification** | Must notify Data Protection Board + affected users upon breach |
| **Children's Data** | Cannot process data of minors under 18 without verifiable parental consent |

### RBI Cyber Incident Reporting
- **Significant cyber incidents** must be reported to RBI within **6 hours of discovery**.
- Followed by a detailed report within **24 hours**.
- Failure to report is a separate regulatory violation.

---

## 8. Quick Reference — Critical Numbers

| Parameter | Value |
|---|---|
| PA minimum net worth at application | ₹15 crore |
| PA minimum net worth by Year 3 | ₹25 crore |
| F&O contract size (post-2024) | ₹15–20 lakh |
| STR filing deadline | 7 working days from suspicion |
| CTR threshold | Cash transactions ≥ ₹10 lakh |
| KYC record retention | Minimum 5 years |
| UPI P2P limit | ₹1 lakh/transaction |
| LRS annual limit | USD 2,50,000 per resident |
| FEMA violation penalty | Up to 3× amount + imprisonment |
| RBI cyber incident notification | Within 6 hours |
| T+1 equity settlement | Trades settle next business day |
