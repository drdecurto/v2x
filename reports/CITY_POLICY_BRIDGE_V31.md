# v31: matched city governance comparison

This package adds 240 completed traffic runs: three cities × twenty existing development seeds × four policies. Demand, message assignments, route candidates and the finite observation trace are matched within blocks. All results are exploratory; known simulator failures remain in the outcomes. The author-requested manuscript text stays unchanged for the concise final rewrite.

## What was coupled

SUMO permission-derived closure observations are sampled every5s and delivered through the native stationary LTE profile6 trace at epoch300s, without looping or time scaling. The consumer rechecks freshness, version and the first-edge route-choice gate before applying a preflighted diversion. Receipt and response processing use0.5s simulation steps. All eligible drivers comply; this is not calibrated behavioral uptake.

The primary remote model, Qwen3-30B-A3B, makes360 offline semantic audits (six constructed categories per block). Each exact verdict and measured request duration is reused for that block/category. The authoritative semantic facts are static closure status and alternative availability; runtime received evidence must match before using the semantic result. This is cached semantic evaluation with discrete-event timing replay, not live per-driver inference or measured load capacity. Audit-result and driver dispatch are assumed colocated with the consumer; only source observations use the empirical transport trace. No5G/6G or urban-radio validation is claimed.

Policies: no content audit; deterministic replacement template; content audit with5s deadline; content audit with template fallback when pending after2s. All receive the same structured detour action. False prose does not become a different action through an unimplemented language parser. Direct semantic-audit acceptance, delivered original text and executed routing are distinct endpoints.

## Outcomes

Totals across twenty demand blocks per city. CO₂ includes unfinished-vehicle emissions accrued by2400s; it excludes their unobserved subsequent travel. Read it jointly with arrivals and unfinished trips.

| City | Policy | Arrivals | Running/pending | CO₂ kg | Applied diversions | Harmful original texts | Clean admitted / clean requests |
|---|---|---:|---:|---:|---:|---:|---:|
| los_angeles | none | 11984 | 16/0 | 13549.38 | 104 | 49 | 30/30 |
| los_angeles | rules | 11984 | 16/0 | 13549.38 | 104 | 0 | 30/30 |
| los_angeles | content | 11975 | 25/0 | 13605.74 | 45 | 0 | 23/30 |
| los_angeles | deadline | 11975 | 25/0 | 13605.74 | 45 | 0 | 23/30 |
| luxembourg | none | 11868 | 131/1 | 10352.43 | 161 | 70 | 62/62 |
| luxembourg | rules | 11868 | 131/1 | 10352.43 | 161 | 0 | 62/62 |
| luxembourg | content | 11891 | 109/0 | 10314.53 | 71 | 0 | 50/62 |
| luxembourg | deadline | 11891 | 109/0 | 10314.53 | 71 | 0 | 50/62 |
| pedralbes | none | 11135 | 408/0 | 10692.32 | 93 | 53 | 28/28 |
| pedralbes | rules | 11135 | 408/0 | 10692.32 | 93 | 0 | 28/28 |
| pedralbes | content | 11175 | 367/1 | 10648.76 | 35 | 2 | 23/28 |
| pedralbes | deadline | 11175 | 367/1 | 10648.76 | 35 | 2 | 23/28 |

## Paired differences against deterministic templates

Mean per demand block; brackets are95% percentile-bootstrap intervals using the frozen10,000resamples and seed8141. Intervals quantify development-seed variability, not independent cities, traces or real-world generalization. No adjustment for multiple exploratory comparisons.

| City | Policy | Δ CO₂ kg | Δ arrivals | Δ harmful texts |
|---|---|---:|---:|---:|
| los_angeles | none | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 2.450 [1.750, 3.150] |
| los_angeles | content | 2.818 [-0.178, 6.231] | -0.450 [-1.250, 0.150] | 0.000 [0.000, 0.000] |
| los_angeles | deadline | 2.818 [-0.178, 6.231] | -0.450 [-1.250, 0.150] | 0.000 [0.000, 0.000] |
| luxembourg | none | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 3.500 [2.850, 4.200] |
| luxembourg | content | -1.895 [-21.028, 13.749] | 1.150 [-5.050, 8.400] | 0.000 [0.000, 0.000] |
| luxembourg | deadline | -1.895 [-21.028, 13.749] | 1.150 [-5.050, 8.400] | 0.000 [0.000, 0.000] |
| pedralbes | none | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 2.650 [1.800, 3.600] |
| pedralbes | content | -2.178 [-29.692, 18.734] | 2.000 [-6.100, 12.550] | 0.100 [0.000, 0.250] |
| pedralbes | deadline | -2.178 [-29.692, 18.734] | 2.000 [-6.100, 12.550] | 0.100 [0.000, 0.250] |

## Retained failures and scope

All600 requested trips per city/block remain accounted for as arrived, running, pending or excluded. Pedralbes preflight exclusions are not replenished. No blocks or unfinished trips are removed. Closure dynamics remain unresolved; small CO₂ differences must not be presented as a general environmental advantage. Road-choice failures, stale/missing observations, superseded audits, expiry, braking and other safety counters are retained in the evidence. Synthetic demand and imported signal timing are not municipal calibration.

Only the initial primary remote model is used in this integrated comparison. The six-model service benchmark remains separate. Category reuse and one finite trace mean request records are not independent semantic/radio trials. Message labels are constructed, not blinded human annotations. The frozen plan used existing known development seeds and was not a confirmatory test plan.

## Validation

Independent verification reconciles every completed block against trip XML/statistics and Decimal CO₂ totals; exact route-file equality is checked within all matched blocks. Every source-observation packet is reconciled to native TX/loss/delay, receipt quantization and source sequence. Consumer decisions are reconstructed from saved deliveries and independent timing/rule arithmetic without calling the production consumer. Applied routes must equal the preflighted alternatives. The before-choice flag is recorded by the runtime and checked for decision consistency; full continuous vehicle trajectories were not captured.

Unfiltered safety and closed-edge occupancy totals are saved separately as safety_totals.json; all per-block counters remain in summary.json.
