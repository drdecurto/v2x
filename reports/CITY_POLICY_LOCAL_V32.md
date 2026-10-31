# v32: local and remote city governance evidence

The primary remote comparison and the local Phi-4 replication are complete. This evidence package retains the manuscript unchanged for the author’s concise rewrite. All comparisons use existing development seeds and known simulator limits; none is a confirmatory field result.

## Main study design

Three map-derived cities, twenty matched demand seeds per city and four policies: no content audit, deterministic template, content audit and a2s timeout-to-template policy. Source observations traverse one finite stationary LTE trace with original timing and losses. SUMO runs for2400s; the incident spans0–900s. All eligible drivers comply. Recorded semantic-audit verdicts and service durations are replayed at actual departure; these are not live per-driver inference or queue/load measurements. Source observations refresh every5s, receipts/decisions are quantized to0.5s and the consumer checks freshness, version and route-choice eligibility.

Two semantic configurations use exactly the same360prompts each: remote Qwen3-30B-A3B and installed local Phi-4. The local follow-up uses nativeJSON/256outputtokens; remote uses promptJSON/1024tokens. Model and inference configurations differ, so this is not a causal edge-versus-cloud placement experiment. The local model was chosen after observing that every remote audit finished before0.85s and could not activate the2s fallback. This sequential research decision is disclosed, not presented as preregistration.

The local study reuses120identical no-audit/template baseline arms with verified hashes; only120additional city runs were needed. Thus there are360unique city runs in the combined two-configuration comparison, not480independent runs. Category-specific cached timings are reused within blocks and are not per-vehicle latency samples.

## Local service measurements

All360planned calls are retained; 0 output/transport failures. Median client duration: 5.826s. Calls at or above2s: 360/360; at or above5s: 276/360. First-call loading is retained. Exact model digest: `ac896e5b8b34a1f4efa7b14d7520725140d5512484457fab45d2a4ea14c69dba`.

## Pooled descriptive service outcomes

Totals across the same60city-demand blocks, for visibility only; city-stratified paired uncertainty remains in the full analysis. Harmful text is defined by constructed reference categories; no independent human labels are claimed.

| Configuration | Policy | Applied diversions | Clean admitted / requests | Harmful original texts | Arrivals | Running/pending |
|---|---|---:|---:|---:|---:|---:|
| Remote primary | none | 358 | 120/120 | 172 | 34987 | 555/1 |
| Remote primary | rules | 358 | 120/120 | 0 | 34987 | 555/1 |
| Remote primary | content | 151 | 96/120 | 2 | 35041 | 501/1 |
| Remote primary | deadline | 151 | 96/120 | 2 | 35041 | 501/1 |
| Local Phi-4 | none | 358 | 120/120 | 172 | 34987 | 555/1 |
| Local Phi-4 | rules | 358 | 120/120 | 0 | 34987 | 555/1 |
| Local Phi-4 | content | 2 | 0/120 | 0 | 35103 | 439/1 |
| Local Phi-4 | deadline | 296 | 104/120 | 0 | 34995 | 547/1 |

## Local paired application outcomes

Mean per demand block relative to the deterministic template; brackets are95% paired percentile-bootstrap intervals over20existing demand seeds (10,000resamples, seed8141). Do not pool cities to hide heterogeneity. CO₂ includes unfinished-vehicle emissions accrued by the horizon, not their eventual journey totals.

| City | Policy | Δ CO₂ kg | Δ completed trips |
|---|---|---:|---:|
| los_angeles | content | 4.108 [1.834, 6.277] | 0.100 [-0.150, 0.450] |
| los_angeles | deadline | 1.006 [-1.843, 4.079] | -0.300 [-1.100, 0.400] |
| luxembourg | content | -5.223 [-20.958, 4.011] | 3.000 [-0.050, 8.700] |
| luxembourg | deadline | -2.634 [-8.303, 1.033] | 0.950 [-0.050, 2.700] |
| pedralbes | content | -2.798 [-31.244, 18.699] | 2.700 [-5.450, 13.200] |
| pedralbes | deadline | 1.566 [-0.308, 4.018] | -0.250 [-0.800, 0.100] |

## What the short manuscript can support

1. Treat semantic auditing and delivery validity as separate checks. The broader six-model benchmark contains freshness, factual and instruction-handling failures; the common consumer independently blocks stale evidence.
2. Compare against deterministic templates. Removing untrusted prose can preserve the predefined route action without inference delay. The benchmark does not measure the usefulness of richer language, so it cannot claim template superiority for every application.
3. Measure timeliness and integrity jointly with traffic outcomes. Waiting for a verdict can miss the route-choice point or encounter a newer observation. The local replication exposes timeout behavior under measured slower service; the remote primary did not.

## What must remain qualified

The six-model180case benchmark is constructed and template-dependent; the city study uses a single primary model and one local follow-up, synthetic uncalibrated demand, imported signals, one reused stationary LTE trace and cached offline semantic audits. Source observations alone traverse the empirical link. No vehicular radio/5G/6G validation, live per-driver service capacity, blinded human validation or general CO₂ benefit follows. Closure-related incomplete trips and safety events remain in all arms. Inspect city-specific CO₂ and completion intervals together before stating an application benefit.

## Author handoff and readiness

The bounded experiments are complete, but the inherited PDF does not contain the new results. A concise rewrite should center on the template baseline, runtime safeguards and timing trade-off, with detailed development chronology in supplementary evidence. Author affiliations, correspondence and declarations still need the authors. Confirmatory field or calibrated traffic claims are unsupported; an honest application-layer exploratory benchmark is the defensible scope. No publishing or submission has occurred.

Validation: all240local-study arms independently reconciled to source hashes, native observation packets, timing/rule arithmetic, applied routes, trip accounting and Decimal emissions. All360local prompt hashes match the remote prompts exactly; exact model digests and120reused baseline hashes checked. Existing before-choice flags are checked for decision consistency, not independently reconstructed from full continuous trajectories.
