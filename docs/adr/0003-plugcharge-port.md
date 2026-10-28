# ADR-0003: One Plug&Charge port, two ecosystem adapters

**Status:** accepted (2026-10-25) · **Date:** 2026-10-24

**Context.** Hubject OPCP and GIREVE PNCP both offer pools (root, provisioning, contract) and a CPS. OPCP distinguishes "MO with own PKI" from "MO with V2G PKI"; PNCP offers a managed "create, build, sign and store" service or enrolment of our own certificates.

**Decision.** `EV_PNC_plugcharge` owns the contract lifecycle (EMAID, PCID binding, renewal, revocation) behind one port. `EV_PNC_roaming-hubs` provides OPCP and PNCP adapters. Whether we run our own PKI or use the hub-managed path is decided in analysis WP6.

**Open.** Cost and contract terms of each managed path; whether one contract certificate per vehicle is enough when both ecosystems are used (the CPO installs one certificate at a time per PNCP §3.6).

**Sources.** OPCP 04_authentication.md, cps.v1.json; PNCP guide §3.7.1, §3.6.

**Evidence added after the deep runs (2026-10-24).**
- GIREVE: "Create CC, build and sign, store in CCP" means the eMSP needs no own MO PKI or HSM; ISO 15118-2 only; mutual TLS since 2026-09-22 (PNCP guide §3.7.1, §3.6.3, §2.5). Fees not public.
- Hubject: MO CA path through the Hubject PKI (EST simpleenroll, generateSignedContractData); fees not public; EMAID prefix must be registered first (OPCP 04_authentication.md).
- GIREVE, Hubject and Irdeto announced access to each other's Plug&Charge networks (GIREVE press release, 2025-06-16), so one contract certificate may reach CPOs in both ecosystems. Scope is unconfirmed.
- Recommendation for the product owner: start with the hub-managed path of one hub behind the port (no own PKI), and choose the hub by price and by which hub the pilot CPOs can fetch contracts from. Own PKI stays a later option.

**Decision update (2026-10-25, accepted).** Use the hub-managed path behind the port; no own PKI or HSM in the pilot. Pre-production starts on GIREVE PNCP ("create, build, sign and store") because it needs no contract with Hubject first. The production hub is chosen at the go/no-go gate (2026-12-07) by which Contract Certificate Pool the pilot CPOs query, then by price (deliverables/07-go-no-go.md, K2 and K6). The port must keep a later move to own PKI possible (hybrid). We still hold the mTLS client key, the OAuth client secret and the OPCP credentials, so the key vault (TR-18) stays in scope. ISO 15118-2 only; EMAID prefix depends on the TR provider ID (TR-03).
