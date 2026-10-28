# Request for Proposal (RFP) Draft
## End-to-End Plug&Charge EV Navigation and Charging Experience Platform
### OCPI 2.2 Integrated Mobile Application (CarPlay Supported)

**Market Focus:** Turkey  
**Date:** 24 October 2026  
**Version:** 1.0 (Draft)  
**Prepared for:** New venture (Turkey & Europe scope)

---

## 1. Introduction and Project Summary

This RFP draft defines the requirements for a new platform that aims to deliver a seamless, end-to-end charging experience for electric vehicle (EV) users in Turkey. The project combines ABRP-style navigation and route planning in a CarPlay-supported mobile application with fully automatic Plug&Charge (ISO 15118) session initiation and payment.

The core objective is that customers should not need to deal with multiple memberships or apps. Once the cable is plugged in, the charging session starts automatically and payment is handled in the background. The system will integrate with CPOs and eMSP roles via **OCPI 2.2**, and will consume real-time socket status and availability data from **EPDK** (Energy Market Regulatory Authority).

---

## 2. Background and Objectives

Current charging ecosystems in Turkey still force users to download separate apps, create accounts, and manage payment methods for different Charge Point Operators (CPOs). This creates significant friction, especially on long-distance trips.

The project aims to solve the following problems:

- Fragmented user experience caused by multiple memberships and apps
- Limited and inconsistent Plug&Charge coverage
- Lack of real-time socket availability integrated into route planning
- Missing secure one-time payment flow for non-registered (guest) users

---

## 3. Project Scope

The project includes the following main components:

1. Mobile application with full **CarPlay** and **Android Auto** support (iOS & Android)
2. ABRP-style route planning, range estimation, and charging stop optimization
3. **OCPI 2.2** based hub/eMSP integration (locations, tariffs, sessions, CDRs with CPOs)
4. End-to-end Plug&Charge session start via **ISO 15118-2 / 15118-20**
5. Real-time socket telemetry from **EPDK** servers (availability, power, status)
6. One-time credit card registration + explicit consent flow for guest users (KVKK compliant)
7. Integration with **OCPP 2.0.1 / 2.1** CSMS for certificate and authorization messages

---

## 4. Functional Requirements

### 4.1 Navigation and Route Planning
- Full route experience on CarPlay and Android Auto
- Range estimation based on vehicle model, battery state, weather, and traffic
- Automatic suggestion of charging stops with real-time EPDK availability check
- Multi-stop routes and alternative route options

### 4.2 Plug&Charge and Payment
- Automatic identification and session start via ISO 15118
- Automatic charging for registered users with stored payment method
- One-time card registration + clear consent text for guest users
- OCPI CDR generation and billing processes

### 4.3 Data and Telemetry
- Nearest socket status from EPDK data sharing / API
- OCPI 2.2 modules: Locations, Tariffs, Sessions, CDRs
- Real-time updates of availability and power information

---

## 5. Technical Requirements

### 5.1 Standards and Protocols

| Component     | Requirement                                                                 |
|---------------|-----------------------------------------------------------------------------|
| **OCPI**      | OCPI 2.2 (hub routing headers, CdrToken, Smart Charging module support)   |
| **OCPP**      | OCPP 2.0.1 / 2.1 (Authorize with eMAID, Get15118EVCertificate, SignCertificate, Security Profile 3) |
| **ISO 15118** | ISO 15118-2 and 15118-20 (Plug&Charge, PKI, OCSP stapling)                 |
| **EPDK**      | Official data sharing / API for telemetry (availability, status)           |
| **Compliance**| KVKK (Turkish Data Protection Law) + PCI-DSS for payments                  |

### 5.2 Other Technical Expectations
- Mutual TLS and secure certificate management (TPM / HSM)
- High availability and scalable backend architecture
- Preparation for AFIR 2027 requirements (support for both ISO 15118-2 and 15118-20)
- Turkey-first deployment with clear path to European expansion

---

## 6. Expected Deliverables

1. Detailed technical architecture document and integration diagrams
2. Working mobile application (MVP: navigation + basic OCPI + Plug&Charge PoC)
3. Pilot integration with EPDK and at least one CPO
4. KVKK compliance report and consent texts
5. Test plan, security audit, and operational documentation

---

## 7. Evaluation Criteria (Draft)

- Proven experience with OCPI 2.2 and ISO 15118 / Plug&Charge
- Quality of CarPlay / navigation integration
- Capability in EPDK and CPO integrations
- Approach to KVKK and security
- Technical team experience and references

---

## 8. Timeline (Draft)

| Phase                        | Duration     | Key Activities                                      | Deliverables                          | Target Completion |
|-----------------------------|--------------|-----------------------------------------------------|---------------------------------------|-------------------|
| **Phase 0 – Discovery**     | 4 weeks      | Requirements finalization, EPDK/CPO outreach        | Updated RFP & architecture outline    | Month 1           |
| **Phase 1 – Foundation**    | 8 weeks      | OCPI 2.2 hub setup, backend core, KVKK framework    | Technical design document             | Month 3           |
| **Phase 2 – MVP Development**| 12 weeks    | Mobile app (CarPlay), route engine, basic Plug&Charge PoC | Working MVP application               | Month 6           |
| **Phase 3 – Pilot**         | 8 weeks      | EPDK telemetry integration + 1 CPO pilot            | Pilot report & feedback               | Month 8           |
| **Phase 4 – Hardening**     | 6 weeks      | Security audit, performance, guest flow polish      | Production-ready release              | Month 10          |
| **Phase 5 – Launch & Scale**| Ongoing      | Public launch in Turkey, additional CPOs            | Live platform                         | Month 11+         |

> **Note:** Timeline is indicative and subject to EPDK data access approval and selected CPO availability.

---

## 9. Next Steps

This document is a draft compiled from the project discussion. The following points are recommended for clarification:

- Target market priority (Turkey first, then Europe?)
- Current status of EPDK data sharing process
- Preferred pilot CPOs and preferred timeline
- Budget range and expected team structure

---

**Document Status:** Draft – Version 1.0  
**Prepared on:** 24 October 2026  
**Market:** Turkey (primary)
