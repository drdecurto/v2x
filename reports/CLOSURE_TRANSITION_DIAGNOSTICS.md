# Closure-transition diagnostics

## Question and selection

The preceding 60-block validation recorded 17 entries after a permission closure and 291 unfinished vehicles. These diagnostics investigate those failures; they are selected using observed development outcomes and cannot estimate their population prevalence or an auditing benefit.

The transition diagnostic reruns every block containing a recorded entry: 13 blocks, all 17 entrants. It preserves the original routes, network, demand seed, 0.5 s steps and closure at 300 s. It observes the affected vehicles from 298 through 305 s and stops before the advisory cohort begins. The original entries occurred from 300.5 through 304 s. No route intervention is scheduled before 310 s, so truncating this diagnostic does not omit an earlier treatment.

A separate control selects the block with most unfinished vehicles in each city, breaking ties by lowest seed: Los Angeles 4211, Luxembourg 4219 and Pedralbes 4219. It removes only the permission closure while retaining the original eligible detours and simulation settings. This is an artificial diagnostic control, not natural driving without an incident, a content-auditing baseline or a random sample.

## Findings

All 17 entry identities and times reproduce exactly. At 300 s, before permissions change, every affected vehicle is on an internal junction lane. Independent network-topology checks establish that each such lane connects to the incident edge. All incident lanes report passenger traffic prohibited after the change. This supports junction clearance as the explanation for these observed entries. It does not establish that every vehicle approaching a closure will be handled safely, or that step sampling detects every possible entry.

| Selected city/seed | Accepted | Running with closure at 2400 s | Running without closure | Identical applied detours |
|---|---:|---:|---:|---|
| Los Angeles / 4211 | 600 | 16 | 0 | Yes |
| Luxembourg / 4219 | 600 | 20 | 0 | Yes |
| Pedralbes / 4219 | 567 | 120 | 0 | Yes |

All accepted trips finish in these three no-closure controls. The exact departure times, vehicle identities and applied routes of the cohort match the corresponding closure runs. No collisions, emergency braking, emergency stops or teleports occur in these controls. Completion differences implicate the closure intervention under these selected conditions, but do not locate the mechanism of persistent queues or establish a representative effect size. The three controls do not cover every emergency-braking case from the preceding 60-block run.

## Consequences for the benchmark

Retain the original 17 entry records and the 291 unfinished vehicles; do not overwrite them or retrospectively declare every closure check passed. A future protocol should distinguish vehicles already on the road, vehicles on connecting internal lanes at activation, and new approach traffic. Junction clearance is part of an operational closure transition, not an instantaneous physical barrier. Any allowed clearance set must be defined from the activation snapshot before later entries are observed.

Before policy comparisons, instrument queues and lane permissions around reopening at 900 s and inspect the unfinished vehicles at the horizon. Investigate braking using matched controls for the affected blocks. Specify a physically interpretable activation/clearance rule and a common treatment of spillback before rerunning all development seeds. Preserve the fixed-horizon joint report of emissions, completion and exclusions; do not make a CO2-saving claim by ignoring unfinished trips.

## Verification and cost

Independent checks reconcile all entry events, input hashes, forbidden passenger permissions, internal-lane topology, control selection, identical route interventions, trip counts, safety statistics and decimal CO2 aggregation. All checks pass, as do the existing 38 tests. These checks establish record consistency and the reported diagnostic facts, not a validated urban deployment. No model calls were made; the API reservation count remains 72. Raw LTE traces were not modified or republished.
