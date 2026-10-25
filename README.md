# EV_PNC_docs

Platform architecture, ADRs, RFP v2, corridor-pilot and go/no-go specs, KVKK/PCI notes, squad working agreement and kanban. Consent and hub-vendor documents live in their own repos.

Part of the **EV_PNC** platform: a neutral eMSP integration layer for Turkey-first, Europe-ready Plug&Charge, navigation and payments. The platform is neither a CPO nor a payment institution.

> Plug in, charging starts, payment completes in the background.

## Scope

- ADR-0001..0006 and later ADRs (copied from the hub analysis, one numbering)
- RFP v2, purpose document (AMAC), corridor-pilot scope, KPIs and spec, go/no-go criteria
- Context map of all EV_PNC_ and EV_PnC_Consent_ repos; packaging check results per release
- Platform KVKK/GDPR data inventory (roaming transfers are owned by EV_PnC_Consent_docs)
- squad/: working agreement, CLAUDE.md template, definition of done, board CSV imports

## Tech stack

Markdown, Mermaid, MkDocs

## Packaging

- Published components: (no published component)
- Depends on: nothing outside this repo
- Depended on by: no repo
- Dependency rules: no cycles (ADP); depend towards more stable components (SDP); published `*-api` components hold abstractions, deployables hold concrete code (SAP). CI runs `tools/packaging_check.py --strict` from `EV_PNC_docs`.
- Owner: Architect agent + Product owner · Wave 1 (now, before the 2026-12-07 gate) · Visibility: public

## Proposed layout

```
docs/{adr,rfp,pilot,compliance,context-map}
squad/
```

## Related

- Plan: `repo-plan/v2/README.md` (project files); consent repos: `EV_PnC_Consent_*` (`repo-plan/consent/README.md`)
- Docs: [EV_PNC_docs](https://github.com/COPUR/EV_PNC_docs)

## Status

Scaffold only. Not production ready.

## License

Apache-2.0 (proposed)
