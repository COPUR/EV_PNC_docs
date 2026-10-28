# Vehicle APIs and digital keys: what Tesla, Togg and BYD expose

**Status:** proposed · **Date:** 2026-10-28 · **Revision:** 0.1 · Companion to [ADR-0019](adr/0019-vehicle-integration-and-digital-key.md) and [02-adapter-design.md](02-adapter-design.md).

## 0. How to read this

Evidence labels follow the earlier hub research (`engineering-briefing/research/re-pnc-hubs-tesla.md`): **F** = fact from an official or primary page we read, **I** = inference, **U** = unknown or not publicly documented. Nothing here comes from touching a live OEM system. Sources were read on 2026-10-28; the web search tool returned only link lists for several queries, so every claim below rests on a page we opened, and the list of pages we could not open is in section 6.

"Reverse engineering" is read the way ADR-0018 reads it for the hubs: derive interfaces from public specifications, official SDKs, public documentation and open-source projects. It does not include breaking an app's protection, intercepting another person's traffic, using someone's credentials without their consent, or minting a vehicle access key the OEM did not issue (section 5).

## 1. Three different things share the name "digital key"

The request mixes three mechanisms. Only the first two matter to an eMSP.

| # | Mechanism | Who issues it | What it does | Does the eMSP need it? |
|---|---|---|---|---|
| A | **Cloud vehicle API** (OAuth grant by the owner) | OEM backend | Read VIN, state of charge (SoC), charging state; sometimes commands | **Yes**: SoC for the planner (P3-01..03), VIN proof for the binding (P2-14) |
| B | **Third-party key enrolled on the vehicle** (Tesla "virtual key") | The owner approves in the OEM app | Lets our backend's key authenticate to the vehicle: signed commands and the vehicle-side Fleet Telemetry configuration | **Yes for Tesla**, because telemetry and commands need it |
| C | **Owner access key** (phone, watch, card: unlock, start, drive) | OEM app or Apple/Google Wallet | Physical access to the car | **No.** Charging needs no access key, and holding one would make us an access-control provider |
| D | ISO 15118 contract certificate (Plug&Charge) | The eMSP's PKI, via the vehicle's contract install | Authorises a charging session | Already covered by ADR-0003; not a digital key |

## 2. Tesla

**Official interface: Fleet API (F).** Third-party OAuth, owner grants scopes per vehicle. Regional endpoints: North America and Asia-Pacific `fleet-api.prd.na.vn.cloud.tesla.com`, Europe/Middle East/Africa `fleet-api.prd.eu.vn.cloud.tesla.com`, China separate (Tesla developer docs, Regions and Countries). Token exchange moved to `fleet-auth.prd.vn.cloud.tesla.com` in 2025 (announcements, 2025-07-21).

**Onboarding (F).** Tesla account with MFA; application registered with legal business details, scopes and purpose; an EC prime256v1 key pair; the public key hosted at `/.well-known/appspecific/com.tesla.3p.public-key.pem` on the application domain (the domain must keep serving it, announcement 2024-02-02); a partner token and a `register` call in each region.

**The "virtual key" (F).** To send commands, the public key must be paired with each vehicle. The owner opens `https://tesla.com/_ak/<domain>`, the Tesla app (4.27.3 or later) shows the domain and asks for approval, and the vehicle must be online and paired with the phone. The vehicle then lists the domain on its Locks screen. The Tesla Vehicle Command SDK (Go, Apache-2.0) signs commands end to end, so a valid OAuth token alone is not enough: the vehicle rejects a command not signed by an enrolled key. Its HTTP proxy converts REST calls into this protocol; `tesla-control` can also reach a nearby vehicle over BLE. The newer protocol does not cover pre-2021 Model S/X, and REST commands were deprecated in 2023-24. Models S/X with the Intel Atom computer need no virtual key and use an owner toggle instead (announcement 2025-06-26).

**Streaming (F).** Fleet Telemetry pushes signals to a server we host; vehicle registration went live 2024-01-02, CSR onboarding was dropped 2024-08-15, and `minimum_delta` / `resend_interval_seconds` limit traffic (2025-01-09). Tesla warns against periodic polling (2023-10-24). Which signals exist (battery level, charge state, location) and their exact names must be pinned from Tesla's field list when the contract is written (U until then).

**Price (F).** Pay per use since 2025-01-01: streaming signals 150,000 per USD, commands 1,000 per USD, REST data 500 per USD, wakes 50 per USD; each Tesla account gets a USD 10 monthly discount (notateslaapp.com summary of Tesla's announcement). A polling design costs about USD 10 per vehicle per month; streaming is the cheap path. **I:** with `minimum_delta` on SoC the streaming cost per vehicle is far below USD 1 a month; measure in the spike.

**Turkey (U, risk).** The Regions page lists the countries where payment and billing limits are available; Turkey is not among them, and the announcements say developers in unsupported countries "were to have limited usage" from January 2025. Whether a Turkish legal entity can register and pay is not stated. Mitigations: ask Tesla through the developer dashboard; register through a legal entity in a listed country; or buy the same data from a Tesla-API aggregator (then it is a processor under KVKK, section 7).

**Plug&Charge (I).** The virtual key does not make Tesla cars Plug&Charge capable at third-party chargers. The earlier research found no public evidence that Teslas present ISO 15118-2 contract certificates to third-party networks; at EVgo they use MAC-address Autocharge. A Tesla linked through Fleet API gives us a verified VIN, not a contract certificate (ADR-0019 §5).

**Gap for the pilot:** none for SoC and VIN, if the Turkey billing question is answered.

## 3. Togg (T10X)

**Official public interface for third parties: none found (U).** Trumore, Togg's app, is described in launch coverage with charging-station maps, route cost estimates and an energy-per-trip estimate; the same coverage names partnerships with more than twenty start-ups but no developer API, SoC or remote-control interface (teknoblog.com, tamindir.com; pre-launch articles, so they may be stale).

**Owner digital key (F).** Trumore's digital key works over Bluetooth, without internet, within about 3 m, and is created in the "Akıllı Cihazım" tab: the owner enters the car with a physical key, opens Settings > Connections > "Erişim Cihazlarım" in the car, taps "Yeni Anahtar Oluştur" in Trumore, and pairs over Bluetooth with a PIN. Sharing: the owner scans a QR code that the recipient's own Trumore app shows ("Dijital Anahtar QR kodumu göster"). The article names NFC and UWB nowhere and names only the T10X (donanimhaber.com). A Trumore user complaint site shows pairing problems exist (sikayetvar.com, anecdotal).

**Consequences.**
- A third party cannot be a key recipient: sharing is person to person between two Trumore accounts. There is no API for our backend or our app to enrol a key.
- We found no public protocol document or open-source client for Trumore (U). Deriving one would mean analysing the app and its servers with no public material to start from, on a national-champion product, with no vehicle of our own to test on. We do not recommend it (section 5).

**What we can do (I).** Identity by VIN and registration document (P2-14, already decided), SoC from the in-car projection source (section 4A), and a partnership request if the product owner wants one (see decisions). Whether Android Auto exposes energy level on the T10X is U.

## 4. BYD

**Official public interface for third parties: none found (U).** BYD's app (BYD Auto Link overseas, a different app in China) offers owner functions; the Home Assistant community states it "doesn't offer a public API" (community.home-assistant.io, a user's integration that works by UI automation).

**Owner digital key (F/I).** BYD vehicles use NFC card keys; BYD added Samsung Galaxy Watch support in 2025 (arenaev.com, propakistani.pk); Apple car-key (NFC) support for BYD was reported (NFC Forum coverage; the page itself did not confirm model or region, so I). Model, region and Turkish availability: U. Google's Wallet digital car key requires the vehicle manufacturer to work with Google (developers.google.com/wallet, F), so a third party cannot enrol into Wallet either.

**Community reverse engineering exists.** `Niek/BYD-re` documents the HTTP crypto path of the overseas Android app (`com.byd.bydautolink`) and the China app: login, vehicle list, real-time status, GPS, an MQTT telemetry channel, and remote control with a control password; the envelope uses white-box AES (Bangcle) and the analysis relied on app version 2.9.1 because newer versions add root and hook detection (F, from the repository text; no licence stated in what we read). `wheregoes/byd-apps` is different: it reverse engineers BYD's internal Android services on the head unit and documents no cloud API (F). We did not run either.

**Why this is not a production path (I).** (1) The login grants the same session that carries remote control, so holding a driver's BYD credentials means holding the ability to unlock or start their car; there is no read-only scope. (2) The client works by defeating white-box encryption and relies on an old app build to avoid root detection; BYD can and does change that. (3) BYD's terms very likely forbid it and may void warranty or ban the account (terms not read: U). (4) The repository has no stated licence, so its code cannot be copied.

**What we can do (I).** VIN and registration document; SoC from the in-car projection source if the head unit exposes it (U); a partnership request if wanted; keep the community work as reading material for a research spike with a team-owned vehicle.

## 4A. A vehicle-independent SoC source: the in-car projection (I, spike)

The Android for Cars App Library offers an energy-level listener through `CarHardwareManager`, and the platform gates it with a car-fuel permission; whether a given Togg or BYD head unit actually reports battery level to Android Auto is up to the OEM (U). If it does, our thin native Android Auto module (Java, ADR-0012) can forward the reading to the app, which sends it to the backend. No OEM credentials are involved. Apple CarPlay has no equivalent that we know of (U). Spike on a real vehicle before counting on it.

## 5. What we will not build

- A client that mints, clones or injects a **vehicle access key** (BLE, NFC, UWB) for Togg, BYD or Tesla outside the OEM-approved flow. Besides the legal exposure, a tool that opens cars without the OEM's authorisation is a theft tool. The CCC Digital Key Release 3 specification is public (UWB plus BLE, NFC for backward compatibility; release 3 v1.1 of 2022 is available to the public per the CCC announcement), but real keys are provisioned by the OEM through Apple/Google Wallet or the OEM app. We may use the public specification in the **simulator** as a test double (card VH-08).
- Storing a driver's BYD or Togg **app password** on our servers or in the app.
- Intercepting traffic of an app on a device or account that is not ours, or defeating root/hook detection or white-box encryption.
- Polling an OEM cloud at a rate its terms prohibit.

## 6. Not verified here

Tesla's field list for Fleet Telemetry and the scopes table; Tesla's terms for Fleet API; whether `charging_manager`-style limited key roles exist (the Vehicle Command README text we read does not mention roles); BYD's and Togg's terms of service; Android Auto energy-level support on Togg and BYD head units; BYD Apple/Google key availability in Türkiye; Togg and BYD privacy notices; the Turkish Copyright Law (FSEK 5846) rule on decompiling for interoperability, which counsel must confirm (the EU model is Software Directive 2009/24/EC art. 6).

## 7. Legal and KVKK flags (for counsel, card P0-04 and TR-05)

| # | Risk | Where | Mitigation in the design |
|---|---|---|---|
| L1 | Breach of OEM terms or app licence; account bans | BYD, Togg community clients | No production use of unofficial clients (ADR-0019 §3) |
| L2 | Unauthorised access to an information system (TCK 243-245) if credentials or protocol are used beyond what the owner authorised | any unofficial client | Official OAuth only; owner consent recorded in the consent family |
| L3 | Circumventing technical protection (white-box crypto, root detection) | BYD-re approach | Out of scope |
| L4 | Decompilation outside the interoperability exception | Togg, BYD | Counsel confirms FSEK limits before any spike on an app binary |
| L5 | VIN, SoC, charging state are personal data when linked to a person; location more so | all | Purpose-bound consent (new purpose `vehicle.read`), scopes minimal, location never requested for the pilot, only references on Kafka (ADR-0013) |
| L6 | Cross-border transfer: Tesla's EMEA servers are outside Türkiye | Tesla | Owner instructs the transfer by authorising Tesla's API; our copy stays in Türkiye; counsel confirms the KVKK art. 9 basis |
| L7 | Aggregator as processor | Tesla (if used) | Data processing agreement, Turkish or EU hosting check |
| L8 | Custody of keys that can command vehicles | Tesla key, any credential | One domain key in a managed secret store behind the proxy; no key or token ever in the mobile app; read-only in v1 |
| L9 | Safety: a wrong command (open charge port, stop charging) | Tesla commands | No commands in v1; later only charging commands, each behind a capability flag and an audit event |
| L10 | Open-source licence | BYD-re, others | Read, do not copy; any reuse needs a licence check |
