# Replicated workload and communication protocol

## Diagnosis and completed construction
The1/7/6 counts came from one development seed and a short trace-aligned request window. Repeating model calls on those same requests cannot create traffic replication. Looping or stretching measured traces cannot create independent radio evidence.

We predeclared20 new demand seeds per city(4201–4220),600 requests each, before generation. All60 blocks retain the same[310,370)s scheduled-departure window. Of36000 requested trips,35543 pass routing/lane preflight; all457 exclusions are in Pedralbes and remain accounted for without replacement.

The first fixed-edge construction exposed incident endpoints in35/60 blocks. It remains saved in runs/replication_cohorts_v1. A separately declared development revision chooses an edge>=60m that is not any accepted-route endpoint, maximizes exposure across ALL accepted demand and breaks ties lexically. It does not optimize the advisory-window count or consult traffic/model outcomes. Every seed remains, including an empty LA cohort.

| City | Blocks | Eligible | Assigned25% | Assigned50% | Assigned100% | Distinct incident edges |
|---|---:|---:|---:|---:|---:|---:|
|Los Angeles|20|104|33|56|104|6|
|Luxembourg|20|161|32|73|161|8|
|Pedralbes|20|94|22|41|94|10|

Counts range0–9,4–11,1–11 per block. They are construction opportunities, not received/executed advice or policy effects. Source XML, deterministic edge ranking, endpoints, request partitions, cohort coverage and per-driver SHA256 draws were independently checked. Alternatives pass necessary lane reachability. Dynamic traffic validation remains necessary. All38 existing tests pass; no new traffic or inference runs were made in this stage.

## Evaluation design and gates
- Execute and validate closure/reopening and route commands before effectiveness runs. Preserve pending/running trips, failed routes, safety events and empty cohorts.
- Pair all four policies on identical demand, route candidates, incidents, traces, signal modes and nested driver compliance draws. No privileged truth or realized-current-call latency may enter decisions.
- Retain native trace ordering and finite support. Treat the two profiles as conditional stationary-LTE scenarios, not60 independent channel recordings. Obtain suitable independent mobility traces before channel-generalization claims.
- Use city-specific paired episode effects as the main uncertainty units. Do not bootstrap packets or drivers as independent experiments. Report city and trace differences before pooling.
- Keep2400s whole-network CO2 and arrived/requested service as joint outcomes. Cohort receipt/admission/execution rates are separate; lower emissions with reduced service are not automatically beneficial.
- Estimate paired development variability, then show precision/minimum-detectable-effect sensitivity for predeclared meaningful effects.359 requests is not itself a power calculation. Do not trim zero-effect or sparse blocks.
- Calibrate inference loading, queueing, service and provider round-trip; use fixed-verdict timing controls. Selective deadlines use only calibration/prior observations.
- Freeze new held-out seed/incident/message families, model digests, prompts, deadlines, exclusions, endpoints and analysis before test outcomes. These60 blocks remain development data.

## Budget gate
No paid calls added:72reservations/USD1.046466 against2000-call/USD100 initial-phase limits. A proposed24-request screening batch across five remote models adds120calls(192total), plus24requests across four local models. Check availability/pricing/reasoning settings/local digests before launch and reserve every paid attempt. This is a proposed bound, not a completed model comparison. Naively expanding359requests across models/traces/uptake can exceed the call cap; do not silently expand it. Reuse only identical requests with explicit fixed-replay labeling, not adaptive claims.

## Article protocol section
New Section5 documents source observation, finite-trace delivery, receiver state, advisory/audit request and response, consumer admission, driver uptake and TraCI execution. It specifies logical fields, version binding, duplicate/reordering handling,5s freshness,0.5s processing quantization, separate advisory expiry, failure/uncertainty handling and template fallback. It states which legs are replayed versus local or HTTP/HTTPS.

No application acknowledgement/retry protocol, cryptographic authentication, standardized binary encoding or downstream radio leg is implied. Current fixtures are not a hardened external-message parser. Custom Python/JSON records are not SAE BSM or ETSI CAM/DENM. A future standards adapter needs field mappings, payload/serialization, security and interoperability tests. Official SUMO, SEE-V2X and ETSI TS103831 sources were verified; see PROTOCOL_SOURCES_20261030.md. LTE evidence does not validate NR/5G/6G.
