# Vehicle integration and digital key (proposal)

Status: proposed · 2026-10-28 · revision 0.1. Nothing here is accepted until the product owner accepts ADR-0019.

| File | What |
|---|---|
| [01-oem-interface-analysis.md](01-oem-interface-analysis.md) | What Tesla, Togg and BYD expose, three meanings of "digital key", what we will not build, legal and KVKK flags |
| [02-adapter-design.md](02-adapter-design.md) | Ports, capability matrix, binding evidence, link state machine, Tesla sequence, events, planner contract, mobile |
| [adr/0019-vehicle-integration-and-digital-key.md](adr/0019-vehicle-integration-and-digital-key.md) | The decision and the open choices |
| [03-cards.md](03-cards.md) | Cards VH-01..VH-08 (proposal, not on the board) |

Short answer: Tesla gets a real integration (Fleet API, own command key, telemetry). Togg and BYD publish nothing a third party may use, so they get identity by registration document, an in-car SoC spike and guided key help; pairing or minting their owner keys is out of scope.
