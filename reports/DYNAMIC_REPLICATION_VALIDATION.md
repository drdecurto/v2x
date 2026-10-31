# Dynamic validation of replicated incident blocks

## Purpose and prospective setup

The 359 statically eligible requests are opportunities, not validated interventions or independent experimental replicates. This stage exercises their alternatives in SUMO before deploying paid models. The saved plan includes all 60 development blocks, including the empty cohort; no block is replaced based on its outcome. It does not change the held-out design because no confirmatory experiment has yet begun.

Each block retains its accepted demand and endpoint-safe incident selected before traffic outcomes. Lane permissions change at 300 s and are restored at 900 s; simulation ends at 2400 s with 0.5 s steps. Every eligible driver is assigned perfect information and full uptake once at actual departure, provided the vehicle remains on its original first edge and the incident is active. This deliberately tests route execution without communication or inference failures. It cannot estimate the benefit of auditing, practical uptake or radio performance. Later paired comparisons must include common information, traffic, incidents and compliance draws.

## Checks and retained failures

The runner records each route assignment, returned route, exception, late decision and missed first-edge decision. It reports arrived, running and pending vehicles, retaining all excluded demand. Trip emissions use the explicit HBEFA3/PC_G_EU6 archetype and sum tripinfo CO2_abs, including unfinished trips; milligrams are divided by one million to obtain kilograms. These are modeled tailpipe totals, not measured real-world emissions or policy savings.

A mid-run closure differs from a closure present before traffic starts. Vehicles already on the incident edge at 300 s are recorded separately and allowed to drain. Subsequent entries are recorded by vehicle and time; they are not silently classified as pre-existing occupants. Step sampling does not establish a continuous physical barrier. Emergency braking, emergency stops, collisions and teleports are retained as separate outcomes. In particular, a zero-collision count does not establish a smooth or realistic closure transition.

Independent verification reconciles each block with its hashed construction, checks conservation of accepted demand, recomputes emissions using decimal arithmetic, and checks applied routes against saved alternatives. A passed record audit does not imply the incident safety checks passed.

## Required next investigation

If entries occur after the permission change, inspect approach and internal-junction states at the transition in a separate diagnostic, preserving this run. Determine whether vehicles were already committed or whether permission enforcement is inadequate. Do not explain the observations by assumption. Likewise, localize braking and stops relative to the transition and compare a matched no-closure diagnostic before attributing them to the incident.

Any revised closure protocol must be documented before rerunning all development blocks; no selective removal of troublesome seeds. Only after execution and transition behavior are defensible should a paired policy pilot estimate variability, uncertainty and meaningful sample-size requirements. The repeated traffic blocks still reuse limited stationary LTE recordings and cannot provide independent urban-radio replication.

## Completed results

All 60 blocks completed. All 359 eligible routes were applied exactly.

| City | Accepted | Applied | Arrived | Running at 2400 s | New closed-edge entries | Emergency stops/braking |
|---|---:|---:|---:|---:|---:|---:|
| Los Angeles | 12000 | 104 | 11980 | 20 | 8 | 4/5 |
| Luxembourg | 12000 | 161 | 11961 | 39 | 3 | 0/0 |
| Pedralbes | 11543 | 94 | 11311 | 232 | 6 | 1/6 |

No pending departures, collisions or teleports. Each city has 21 vehicles already on the incident edge at closure, summed across its 20 blocks. All 457 exclusions are in Pedralbes. Independent record verification passes; incident-transition validation remains unresolved. Existing 38 tests pass. No inference calls; reservation count remains 72. Signal detector coverage warnings persist.
