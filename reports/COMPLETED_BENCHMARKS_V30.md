# Completed experiments: evidence update v30

The manuscript text remains v29 for the author’s concise rewrite. These results are exploratory development evidence, not a confirmatory city-level auditing study. No new citations or provider calls were needed for analysis.

## Six model configurations, 180 cases each

Ten constructed evidence worlds × six categories × three wording forms. These are dependent templates, not 180 independent semantic families. The uncertainty rule was fixed before calls: stating that evidence is missing is acceptable; asking to resolve an unobserved outcome requires unsure. Labels are programmatically constructed, not human annotations.

| Model/configuration | Clean | Contradiction | Unsupported numeric | Unresolved question | Injection | Stale | Parse failures | Median client s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3-30B-A3B-Instruct-2507 (prompt JSON) | 30/30 | 30/30 | 30/30 | 24/30 | 30/30 | 0/30 | 0 | 0.597 |
| nvidia/nemotron-3-super-120b-a12b (prompt JSON) | 30/30 | 30/30 | 30/30 | 10/30 | 21/30 | 30/30 | 0 | 1.712 |
| openai/gpt-oss-120b (prompt JSON) | 30/30 | 30/30 | 28/30 | 2/30 | 6/30 | 30/30 | 0 | 0.447 |
| llama3.1:8b (native JSON) | 30/30 | 6/30 | 30/30 | 30/30 | 30/30 | 11/30 | 0 | 1.756 |
| phi4:latest (native JSON) | 30/30 | 30/30 | 30/30 | 30/30 | 28/30 | 0/30 | 0 | 6.607 |
| qwen2.5:14b (native JSON) | 25/30 | 30/30 | 30/30 | 30/30 | 30/30 | 3/30 | 0 | 3.728 |

The original prompt-only Llama arm stopped after three non-JSON outputs; all three remain failures in its separate record. The later native-JSON local experiment is an explicitly revised configuration, not a randomized format comparison. Native JSON constrains syntax, not factual accuracy. Local inference overlapped SUMO execution; remote/local models and output budgets differ. Do not infer an edge-versus-cloud placement effect or hardware-normalized speed ranking.

## Matched application sensitivity

Twenty existing development demand seeds per city; identical route files within each pair; closure before departures, reopening at 900 s, horizon 2400 s. Full diversion affects only the predefined eligible cohort. Twelve identical previous full-diversion blocks were reused with hashes; 108 new blocks complete the 120-arm design. This is routing sensitivity, not a content-auditor comparison.

Full-diversion minus no-diversion mean per demand block; brackets are the frozen 95% paired percentile-bootstrap intervals (10,000 resamples). They describe variation over these synthetic demand seeds, not uncertainty across real cities or radio deployments.

| City | Δ CO₂ kg | Δ completed trips | No-diversion arrivals/running/pending | Full-diversion arrivals/running/pending |
|---|---:|---:|---|---|
| los_angeles | -4.11 [-6.28, -1.83] | -0.10 [-0.45, 0.15] | 11986/14/0 | 11984/16/0 |
| luxembourg | 5.16 [-4.06, 20.90] | -3.00 [-8.70, 0.05] | 11928/72/0 | 11868/131/1 |
| pedralbes | 2.80 [-18.70, 31.23] | -2.70 [-13.20, 5.35] | 11189/353/1 | 11135/408/0 |

Los Angeles has a lower mean modeled CO₂ total with diversion. Luxembourg and Pedralbes do not establish a reduction; their intervals span zero. Completion changes and persistent incomplete trips prohibit interpreting a smaller finite-horizon emissions total as an unconditional environmental benefit. Trip-device totals include emissions from unfinished vehicles, but not their unobserved future travel. The 457 excluded Pedralbes requests per arm remain in the demand accounting. Networks, signals and demand are uncalibrated; closure failures are retained.

## Common safeguards and finite response-path replay

12,960 paired policy records: six configurations × 180 cases × four policies × ideal / stationary LTE profile 1 / stationary LTE profile 6. Initial evidence is already available, exactly as in the model input; no fresh observations arrive during an individual request. Each arm transmits its result using the first native recorded packet opportunity after readiness. Losses and receive delays are preserved with one transmission and no retry, looping or synthetic replacements. This reuses empirical transport timing; it is not an actual network deployment, a simultaneous-load simulation, a complete observation/advisory exchange, or 5G/6G validation.

Content waits at most 5 s. The deadline policy uses the model output if available before 2 s; otherwise it emits a verified template at 2 s. This is offline event replay with measured service durations, not another live asynchronous timing experiment. All arms recheck freshness and expiry at delivery; the earlier live timer experiment remains separate. Structured action/status fields are correct across all prose categories, so contradictions inside the text remain a content-audit task.

Profile 6: each cell is clean actions admitted / rejected-reference original texts delivered. Denominators are 30 clean and 120 reject-labeled cases per model. Unresolved questions are reported separately in machine-readable results, not counted as violations.

| Model | No content audit | Template | Content | Timeout fallback |
|---|---:|---:|---:|---:|
| Qwen/Qwen3-30B-A3B-Instruct-2507 | 21 / 63 | 21 / 0 | 21 / 0 | 21 / 0 |
| llama3.1:8b | 21 / 63 | 21 / 0 | 20 / 18 | 22 / 16 |
| nvidia/nemotron-3-super-120b-a12b | 21 / 63 | 21 / 0 | 23 / 6 | 22 / 2 |
| openai/gpt-oss-120b | 21 / 63 | 21 / 0 | 18 / 16 | 18 / 16 |
| phi4:latest | 21 / 63 | 21 / 0 | 0 / 0 | 22 / 0 |
| qwen2.5:14b | 21 / 63 | 21 / 0 | 12 / 0 | 22 / 0 |

All stale cases are blocked by the common consumer in every arm, despite model-level stale-evidence errors. Templates deliver none of the untrusted original prose by construction. Any advantage of content auditing must therefore be justified against this strong baseline, including information preserved and false rejections; these tests do not establish a net advantage over templates. Loss and delayed readiness can change which native packet is selected, so longer processing can occasionally encounter a received packet where an immediate response was lost. Do not interpret that artifact as a latency benefit. Two reused trace segments and ten constructed worlds are not thousands of independent experimental units.

## Validation and remaining scope

All 120 city result records were independently reconciled to trip XML, running/pending counts and Decimal emission sums; all 60 paired route inputs match exactly. The 12,960 policy decisions were checked by independent event arithmetic without calling the production consumer, including native packet selection and model-independent baseline equality. Source hashes, response parsing and case completeness were checked. Existing 38 tests pass.

The remaining central gap is a matched end-to-end city comparison of the four governance policies with transported observations and actual or explicitly replayed inference. The current evidence establishes component error modes, guarded service behavior and application sensitivity separately. It does not establish that LLM auditing reduces urban CO₂ or improves real traffic. Preserve this limit in the short manuscript.

Cumulative ledger: 612 remote reservations, USD 11.496267 conservatively reserved, within 2000-call/USD100 phase limits. These are reservations, not billed cost. No worker remains active from these experiments.
