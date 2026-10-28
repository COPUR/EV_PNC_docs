# ADR-0019: Vehicle integration and digital-key support (Tesla official, Togg and BYD guided)

**Status:** proposed · **Date:** 2026-10-28 · **Revision:** 0.1 · Accepted by the product owner on the Kanban card for this ADR. Numbering: 0016 and 0017 stay reserved (P0-05, V-01); 0018 is the hub adapter framework.

## Context

The product owner asked for vehicle integration through vehicle APIs, such as Tesla Fleet API, and for digital-key pairing support for Togg, Tesla and BYD, using reverse engineering where no public specification exists. The PSP header keys in their earlier message were only an example. The planner needs the state of charge (SoC) of the car (P3-01..03), the binding needs verified vehicle identity (P2-14, ADR-0007), and Plug&Charge is ISO 15118 (ADR-0003). Already decided and kept: VIN and registration document as the pilot binding; Java and Go backend, planner in Go, React Native mobile with thin native modules; no personal data on Kafka (ADR-0013); consent family as the record (ADR-0007).

Facts (details and sources in [01-oem-interface-analysis.md](../01-oem-interface-analysis.md)): Tesla publishes an official third-party Fleet API with OAuth, an enrolled public key per vehicle and a streaming telemetry service, priced per use; Turkey is not on the list of countries with payment support. Togg and BYD publish no third-party API that we found, and their owner keys (Trumore BLE key, BYD NFC/watch key, Apple/Google Wallet) are issued by the OEM or by Wallet with the OEM. A community project documents BYD's cloud protocol by breaking the app's white-box encryption and relies on an old app build to avoid root detection.

## Options

- **A. Official interfaces only.** Tesla via Fleet API; Togg and BYD via VIN and registration document, in-car projection and OEM partnership if wanted.
- **B. A plus community-reverse-engineered cloud clients** for BYD and Togg in production, holding the drivers' app credentials.
- **C. B plus a self-made BLE/NFC/UWB key client** for Togg and BYD.

## Decision

Option **A**. Option B is allowed as a **research spike only** (section 3); option C is rejected.

1. **Scope of "digital key".** The platform supports (a) cloud vehicle data and (b) for Tesla, enrolling **its own** command key on the vehicle. It does not issue, clone or hold owner access keys for any OEM (analysis section 5).
2. **Adapter framework** like ADR-0018: module `vehicle-core` (ports, `VehicleCapability` matrix, `FailureClass`, `VehicleAdapterContract`), `vehicle-tesla`, and `vehicle-togg` and `vehicle-byd` as capability-empty adapters that only carry the identity-by-document path and the guide content until an official source exists. Rules as pinned data under `contracts/`. Details in [02-adapter-design.md](../02-adapter-design.md).
3. **Reverse engineering, defined.** Allowed: reading public documentation, official SDKs, published specifications (for example CCC Digital Key Release 3, ISO 15118) and open-source projects; observing a **team-owned** vehicle and **team-owned** account; writing the findings as an interface description. Not allowed in production or in the app: defeating encryption or anti-tamper (white-box AES, root/hook detection), storing a driver's OEM app password, intercepting traffic of accounts or devices we do not own, and copying code with no licence. A spike on a third-party app binary starts only after counsel confirms the interoperability rule (analysis L4) and uses a team-owned vehicle.
4. **Credentials.** OAuth refresh tokens are encrypted in the `vehicle-gateway` token vault; the Tesla command key lives only in `tesla-edge` behind a managed secret store. The mobile app holds none of them. The key is domain-wide, so its loss affects every linked Tesla: rotation procedure and an alert on use outside the proxy are part of card VH-02.
5. **Binding and Plug&Charge.** `VehicleBinding` gets an `evidence` attribute (`user_entered`, `document_verified`, `oem_authorized`). A Tesla linked through Fleet API gives `oem_authorized` after the VIN matches the registration document. This does **not** make Teslas Plug&Charge capable at third-party chargers; a Tesla session at a CPO uses the VIN/MAC-keyed identification route researched earlier (EVgo-style Autocharge), which is a separate card (VH-07) and not an ISO 15118 contract install.
6. **Data.** SoC and charging state travel on `ev.vehicle.soc-observed.v1` with `vehicleRef`; VIN, plate and location never reach a topic (ADR-0013 §3, §8). New consent purpose `vehicle.read`, requested in the app before any OAuth hop and recorded in the consent family. Scopes: SoC and charging state only; no location scope in v1; no commands in v1.
7. **Streaming over polling** for Tesla; a REST read only on a user action when the last reading is older than 10 minutes; monthly API budget per account with an alert; Fleet API cost is a line in the pilot budget (K6).
8. **Mobile.** React Native screens for linking and for guide content; Android Auto SoC through a thin Java module when the head unit reports it (spike, VH-06); no key material in the app.
9. **Turkey billing for Tesla Fleet API** is a pre-condition. Order of fallback: ask Tesla through the developer dashboard; register through an entity in a supported country; buy the data from an aggregator under a processing agreement. Decided on card VH-01 before code starts.

## Consequences

- Togg and BYD drivers get no cloud SoC from us until the OEM gives an official path; they enter SoC by hand or through the in-car source. The planner treats `confidence` and age explicitly.
- Tesla drivers get automatic SoC and a verified-VIN binding; Tesla can still revoke or reprice the API.
- "Digital key support" for Togg and BYD is guidance (where the owner's key lives, how to share it with a household member) and a test double in the simulator; it is not pairing by us. If the product owner wants real third-party keys, the only route is an OEM partnership, which needs a decision and is outside this ADR.
- Legal risks L1..L10 in the analysis go to counsel (P0-04) and to the DPO review (X-09, TR-05). Nothing here is legal advice.
- New repository `EV_PNC_vehicle-gateway` and a Go service `tesla-edge`; the user creates the repository. Cards VH-01..VH-08 are proposals; the wartime rule means none is added to the board until the product owner names what to drop.

## Open decisions for the product owner

1. Production use of community-reverse-engineered clients for BYD or Togg: recommended **no** (research spike only).
2. Partnership requests to Togg and BYD (not sent; the hub-email decision of 2026-10-27 covers only Hubject and GIREVE): recommended yes after the gate, as a business request, if real SoC for those brands matters to the pilot.
3. Tesla Fleet API registration route (VH-01).
4. New repository `EV_PNC_vehicle-gateway` or modules inside `EV_PNC_hub-gateway`: recommended a new repository, because the failure and data classes differ from hubs.

## Sources

Tesla Fleet API docs (announcements, regions and countries, getting started), `teslamotors/vehicle-command`, notateslaapp.com on pricing; donanimhaber.com on the Trumore digital key; community.home-assistant.io, `Niek/BYD-re`, `wheregoes/byd-apps` for BYD; CCC Digital Key Release 3 announcements; Google Wallet digital car key overview; skills `architecture-review`, `api-design-and-security`, `microservices-and-ddd`. Earlier research: `engineering-briefing/research/re-pnc-hubs-tesla.md`.
