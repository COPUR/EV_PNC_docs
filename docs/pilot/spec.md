# Spec: İstanbul–Bodrum corridor pilot

**Status:** draft, 2026-10-25 · **Scope:** `scope.md` · **KPIs:** `kpis.md` · **Gate:** `go-no-go.md`
**Owning repos:** `EV_PNC_planner`, `EV_PNC_telemetry`, `EV_PNC_ocpi-emsp`, `EV_PNC_plugcharge`, `EV_PNC_payments`, `EV_PNC_mobile`

Requirement IDs: `CP-<AREA>-NNN`. Confidence: `fact` (sourced), `user` (product owner's scope, accepted 2026-10-25), `inference`. Every requirement names its acceptance file or runbook.

## Requirements

### CP-GEO-001
THE planner SHALL model the corridor as one main route (M: İstanbul → O-5 → Manisa/İzmir → Söke → Milas → Bodrum, with the Didim link) and four alternative families (A1 Çanakkale, A2 southern variants, A3 inland and short detours, A4 Bodrum final segment + Didim), each stored as versioned route geometry with a family code.
- source: scope.md §1
- confidence: user
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-GEO-002
THE planner SHALL tag every EVSE within 2 km of a corridor geometry with the family codes it serves and with a cluster label (for example an Oksijen cluster) so KPIs can be split by family and cluster.
- source: kpis.md "Genel ölçüm kuralları"
- confidence: user
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-GEO-003
THE pilot SHALL run real trips on the main route and on at least three alternative families, including peak-period trips, before any KPI is reported as final.
- source: scope.md §1
- confidence: user
- priority: pilot
- verify: runbook check: trip log per family in the pilot report

### CP-NAV-001
WHEN the driver plans a trip THE planner SHALL rank candidate plans by total time = driving time + predicted charging time + predicted queue time, and SHALL show each component separately.
- source: scope.md §2 F1
- confidence: user
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-NAV-002
THE planner SHALL predict charging time from the vehicle's charging curve, the EVSE's maximum power, the expected power-sharing reduction at that site and the arrival state of charge, and SHALL add a climate-load correction for the final segment in summer.
- source: scope.md §2 F1, §1 A4 (air-conditioning load)
- confidence: inference
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-NAV-003
WHILE a trip is active THE planner SHALL re-plan when the predicted total time of the current plan exceeds the best alternative by more than [5] minutes or when the next planned EVSE becomes unavailable.
- source: scope.md §2 F1, F5
- confidence: inference
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-NAV-004
THE planner SHALL NOT always prefer the nearest EVSE; it SHALL choose the stop with the lowest total time, and on sparse segments (A1) SHALL keep a reserve state of charge of at least [15]% at the next viable stop.
- source: scope.md §1 A1
- confidence: user
- priority: pilot
- verify: acceptance/corridor-planning.feature

### CP-NAV-005
WHERE a segment depends on a ferry or a toll bridge (A1) THE planner SHALL add the predicted crossing wait to driving time and SHALL offer the bridge/ferry alternative with the lower total time.
- source: scope.md §1 A1
- confidence: user
- priority: later
- verify: acceptance/corridor-planning.feature

### CP-IDLE-001
THE planner SHALL predict queue time per EVSE group from live status when available and from historical occupancy by weekday, hour and season otherwise, and SHALL label the prediction source (live or historical) in the app.
- source: scope.md §2 F2, F7
- confidence: user
- priority: pilot
- verify: acceptance/idle-waiting.feature

### CP-IDLE-002
WHEN the predicted queue at the planned stop exceeds [10] minutes (peak [15]) THE app SHALL offer an alternative stop or family with lower total time before the driver reaches the stop.
- source: kpis.md KPI-1, KPI-4
- confidence: user
- priority: pilot
- verify: acceptance/idle-waiting.feature

### CP-IDLE-003
WHEN our driver's session reaches the CPO-published end condition (for DC, 85% state of charge or above when the CPO applies the rule) or the vehicle stops drawing power THE app SHALL notify the driver to move the vehicle, and SHALL show any occupancy or reservation fee the CPO publishes.
- source: Şarj Hizmeti Yönetmeliği amendment, Resmî Gazete 2026-03-23 (secondary: rekabetregulasyon.com, ntv.com.tr); scope.md §2 F2
- confidence: fact
- priority: pilot
- verify: acceptance/idle-waiting.feature

### CP-IDLE-004
THE telemetry service SHALL record per EVSE group the number of simultaneous sessions and their delivered power so power sharing can be modelled (KPI-6).
- source: kpis.md KPI-6
- confidence: user
- priority: pilot
- verify: acceptance/data-foundation.feature

### CP-PNC-001
THE platform SHALL record every Plug&Charge attempt with EVSE, CPO, contract certificate pool used, ISO 15118 version, timestamps (plug-in, authorization, energy flow) and outcome.
- source: kpis.md KPI-3
- confidence: user
- priority: pilot
- verify: acceptance/pnc-friction.feature

### CP-PNC-002
WHEN a Plug&Charge attempt fails THE platform SHALL classify the cause as certificate not found, certificate expired or revoked, pool not reachable, EVSE software, authorization rejected, or other, and SHALL offer the driver an app or guest start within the same screen.
- source: kpis.md "İkincil göstergeler"
- confidence: inference
- priority: pilot
- verify: acceptance/pnc-friction.feature

### CP-PNC-003
THE planner SHALL rank EVSEs that support ISO 15118-2 Plug&Charge for our contract higher only when the driver has an active contract certificate, and SHALL not let this preference add more than [3] minutes of total time.
- source: scope.md §2 F3
- confidence: inference
- priority: pilot
- verify: acceptance/pnc-friction.feature

### CP-ACCESS-001
THE platform SHALL offer every corridor EVSE through one of three channels, in this order: Hubject (OICP, ZES), bilateral OCPI 2.2.1, or guest AD_HOC_USER; the app SHALL show which channel applies before the session starts.
- source: scope.md §2 F4; ../adr/0005-hub-sequencing.md
- confidence: user
- priority: pilot
- verify: acceptance/multi-operator.feature

### CP-ACCESS-002
WHEN an EVSE is reachable through more than one channel THE platform SHALL pick the channel with the lower guest price and, at equal price, the one with live status.
- source: inference from ADR-0006
- confidence: inference
- priority: pilot
- verify: acceptance/multi-operator.feature

### CP-ACCESS-003
THE platform SHALL count reachable EVSEs per channel, per family and per power class (AC, DC < 150 kW, DC ≥ 150 kW) daily, as the K1 evidence for the gate.
- source: go-no-go.md K1
- confidence: user
- priority: pilot
- verify: acceptance/multi-operator.feature

### CP-PEAK-001
THE platform SHALL keep a configurable peak calendar (summer season and each bayram with ±2 days) and SHALL tag every trip, session and KPI sample as peak or normal.
- source: kpis.md "Genel ölçüm kuralları"
- confidence: user
- priority: pilot
- verify: acceptance/idle-waiting.feature

### CP-PEAK-002
WHILE the peak calendar is active THE planner SHALL use the peak occupancy profile for queue prediction and SHALL show at least one alternative-family plan for every trip longer than [200] km.
- source: scope.md §2 F5
- confidence: user
- priority: pilot
- verify: acceptance/idle-waiting.feature

### CP-PRICE-001
THE platform SHALL compute the guest price per EVSE with the ADR-0006 formula (B2B energy price + non-energy components per reference session kWh, × (1 + margin) × (1 + VAT)), in TL/kWh only, and SHALL keep the price fixed from session start to session end.
- source: ../adr/0006-guest-pricing.md; Şarj Hizmeti Yönetmeliği amendment 2026-03-23 (secondary)
- confidence: fact
- priority: pilot
- verify: acceptance/guest-pricing.feature

### CP-PRICE-002
THE platform SHALL reject a margin above [20]% until TR-06 confirms the tier rule, and SHALL flag any EVSE where the guest price exceeds the CPO's direct card price by more than 15%.
- source: go-no-go.md K8 (updated 2026-10-25)
- confidence: user
- priority: pilot
- verify: acceptance/guest-pricing.feature

### CP-PRICE-003
THE platform SHALL collect the direct card price of each corridor DC EVSE (from the CPO's published prices or a field check) at least weekly, so the competition test compares like with like.
- source: kpis.md "İkincil göstergeler"
- confidence: inference
- priority: pilot
- verify: runbook check: weekly price sheet in the pilot report

### CP-DATA-001
THE telemetry service SHALL ingest live EVSE status and power availability from every channel that provides it (OCPI Locations push or pull, Hubject PullEvseStatus) and SHALL mark a status as live only when it is younger than 15 minutes.
- source: kpis.md KPI-7
- confidence: user
- priority: pilot
- verify: acceptance/data-foundation.feature

### CP-DATA-002
THE telemetry service SHALL record status changes, faults and outage durations as an append-only history with EVSE id, timestamp and source, and SHALL keep it for at least two seasons.
- source: scope.md §2 F7
- confidence: user
- priority: pilot
- verify: acceptance/data-foundation.feature

### CP-DATA-003
THE telemetry service SHALL build historical queue and occupancy profiles per EVSE group by weekday, hour and peak/normal, from session data and app-reported arrivals.
- source: scope.md §2 F7
- confidence: user
- priority: pilot
- verify: acceptance/data-foundation.feature

### CP-DATA-004
THE platform SHALL reconcile its corridor EVSE list weekly against the EPDK charging-station list and Şarj@TR, and SHALL raise a discrepancy for missing stations, wrong coordinates, wrong power or wrong connector types.
- source: https://www.epdk.gov.tr/Detay/Icerik/3-0-226/web-servisler (station list REST service); (hub analysis) 03-turkiye-todo.md TR-24
- confidence: fact
- priority: pilot
- verify: acceptance/data-foundation.feature

### CP-DATA-005
THE platform SHALL compute KPI-7 (share of K1 EVSEs with live status and power) daily, per family and channel.
- source: kpis.md KPI-7
- confidence: user
- priority: pilot
- verify: acceptance/kpi-measurement.feature

### CP-KPI-001
THE platform SHALL compute KPI-1 to KPI-7 with the formulas in kpis.md, split by family, cluster and peak/normal, and SHALL publish them on the pilot dashboard daily.
- source: kpis.md
- confidence: user
- priority: pilot
- verify: acceptance/kpi-measurement.feature

### CP-KPI-002
THE platform SHALL support a control group (optimisation off) and a treatment group, assigned per driver at enrolment, and SHALL report each KPI per group.
- source: kpis.md "Genel ölçüm kuralları"
- confidence: inference
- priority: pilot
- verify: acceptance/kpi-measurement.feature

### CP-KPI-003
WHEN a trip ends THE app SHALL ask the driver one optional question on waiting time at each stop, and SHALL store the answer next to the measured waiting time.
- source: kpis.md KPI-1
- confidence: user
- priority: pilot
- verify: acceptance/kpi-measurement.feature

### CP-KPI-004
THE platform SHALL compute KPIs on pseudonymous trip IDs and SHALL reduce stored location traces to H3 resolution 8 cells after 90 days, subject to the KVKK retention policy.
- source: kpis.md "Genel ölçüm kuralları"; (hub analysis) 03-turkiye-todo.md TR-05
- confidence: inference
- priority: pilot
- verify: acceptance/kpi-measurement.feature
