# Environmental consequences of timely, trustworthy mobility advice

Status: prospective design, not a frozen confirmatory protocol. Created before environmental-advisory policy outcomes. The CO2 accounting checks use existing development seed4101 only. No test-set results have been inspected. Do not describe this document as preregistration.

## Question and contribution hypothesis
When does preventing unsupported or obsolete mobility advice improve network-wide modelled CO2, and when do audit delay, unnecessary rejection or collective diversion erase that benefit? The candidate contribution joins received-evidence integrity, response timing and driver uptake with traffic/environmental outcomes. It is not a claim of being the first study; focused related-work verification remains required.

## Common conditions
Use the common three-city OSM construction and preserve all requested, preflight-rejected, pending, running and arrived vehicle IDs. Signal mode is held identical across all policy arms within each block; actuated remains the reference with disclosed coverage limitations, fixed-time is a separate sensitivity. Never select signal mode using the auditing outcome. One shared routing algorithm, candidate route set and incident schedule per paired block. Advisory sensors do not control traffic lights.

The initial emission archetype is HBEFA3/PC_G_EU6, homogeneous gasoline Euro6 passenger cars. This is a controlled model assumption, including for Los Angeles, not a representative local fleet. Add PC_D_EU6 as a prespecified model-class sensitivity before confirmatory execution. No EV/lifecycle/inference-carbon claims in this first stage.

## Policies and information boundary
1. No semantic audit: common expiry, route-executability and evidence-availability gates still apply.
2. Deterministic consistency checks with verified templates: no unverified numerical environmental promises.
3. Audit every eligible advisory: use only received roadside evidence and explicitly labelled route estimates available at issuance.
4. Selective audit: deterministic/template path for supported structured facts; semantic audit for ambiguous free text or unsupported promises, only when a deadline predictor fitted on development latency permits. Otherwise use the current verified template or withhold.

All arms share received observations, compliance assignments, route candidates and action gates. Neither router nor auditor may read future simulator states, paired counterfactual outcomes or realised current-call latency. Separate logs: source truth, transported evidence, predictions, message, verdict, final instruction and evaluation outcomes.

## Message families
Use four families with distinct claim-time labels: accurate road facts; unsupported numerical environmental savings; contradicted road facts; qualified predictions whose outcome is uncertain. Add an obsolete-but-originally-supported message after a source-state change. A future outcome cannot retroactively make an unsupported promise justified at issuance. Correct claim assessment and realised routing benefit are separate endpoints. No source record may contain instructions from message text.

Construct initial development fixtures, then hold out wording and incident combinations, not merely random seeds. Human review of a bounded sample is needed before publication; do not fabricate human validation or treat model agreement as human ground truth.

## Driver uptake and collective effects
Prespecify compliance levels25%,50%,100%. Use one reproducible uniform draw per driver and seed, shared across policies; nested threshold membership ensures pairing. Distinguish assigned compliance, advice receipt, admission and actual route execution. Packet loss and missed decision points can prevent action by an otherwise compliant driver. Report diversion concentration and emissions on affected corridors as secondary outcomes.

## Endpoints and accounting
Primary environmental endpoint: total modelled tailpipe CO2 over the common2400s horizon, including running vehicles, in kg. Co-primary service endpoint: arrived/requested fraction; report excluded, pending and running counts separately. A lower emissions total with less delivered service is not automatically beneficial. Secondary: network travel/waiting time accrued by horizon, completed-trip metrics explicitly conditional on completion, per-driver outcome distribution, route distance, false rejection, unsupported admission, stale admission, audit-deadline misses and executed instructions.

Primary totals use the emissions device tripinfo CO2_abs, including unfinished output, converted from mg to kg by dividing by1e6. Independently sum these fields with decimal arithmetic. Per-step mg/s integrations are a separate diagnostic: development checks found non-identical output/event conventions, so do not assert exact equivalence or mix them. The failed original reconciliation and accounting amendment are preserved in runs/co2_accounting_v1. No emissions imputation for never-departed or excluded vehicles; keep them in the service denominator. Follow-up full-drain sensitivity, if used, must have a common bounded stopping rule and retain unresolved vehicles. Never compare completed-trip means alone.

## Experimental progression and freeze gate
A. Validate accounting on existing development city trajectories; retain adverse static-signal outcomes.
B. Connect actual city incident/route choices to the observation-only consumer and test claim families without paid inference.
C. Calibrate selective deadlines and compare provider/model capability under the existing USD100 phase and2000-call caps, including all72 existing reservations. No automatic expansion. Model choice, exact prompts, revision/digest, timeout and queue limits must be saved before held-out tests.
D. Freeze a machine-readable manifest with hashes of scenarios, messages, models, receiver logic, emission classes, seeds, trace windows, compliance draws, budget and analysis script. Until then no confirmatory run is permitted. Choose sample size from paired development variability and a stated meaningful CO2/service difference; do not invent a power claim now.
E. Use paired episode blocks as the uncertainty unit, clustering by reused trace session where appropriate. Packets, vehicles and repeated model calls are not independent episodes. Preserve null and unfavorable outcomes.

## Communication scope
Native stationary SEE-V2X LTE packet replay remains a sensitivity condition. Paired outdoor mobility traces and synchronization/reuse checks remain unresolved. Do not claim5G/6G validation. Local/remote inference durations include their respective execution paths; do not add an Internet trace on top of measured provider round-trip and double-count it.

## Verified documentation
- https://sumo.dlr.de/docs/Simulation/Output/EmissionOutput.html
- https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html
- https://sumo.dlr.de/docs/Models/Emissions/HBEFA3-based.html
Checked2026-10-30. SUMO emissions are modelled estimates, not physical exhaust measurements.
