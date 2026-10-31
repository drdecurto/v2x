# Reopening diagnostics

The three previously selected maximum-unfinished development blocks were rerun with passive state recording. Selection is outcome-dependent and cannot estimate population effects. No audit, radio or model inference was added. All previous route interventions, demand, closure/reopening times and horizon were preserved.

## Observations

The complete summary records and route-decision logs reproduce the original runs exactly. Restored lane restrictions at900s match each lane's saved restrictions before closure. A failure to restore the incident lane's permissions is therefore not supported as the explanation in these three runs.

| City/seed | Active at900s | Active at2400s | Stopped at2400s | Stopped within1m of lane end with no link to next route edge |
|---|---:|---:|---:|---:|
|los_angeles/4211|222|16|16|2|
|luxembourg/4219|222|20|20|0|
|pedralbes/4219|257|120|120|0|

Two Los Angeles vehicles are stopped at lane ends without a connection from their current lane to the next route edge. This is a local lane-position incompatibility despite the earlier route-level feasibility check. It does not by itself prove that these two vehicles explain every queued vehicle. Luxembourg and Pedralbes have no vehicles satisfying this particular screen; their blockage mechanisms remain unresolved. A TraCI leader query returning no leader is not proof of an unblocked junction: conflict checks, lane-change constraints and internal-junction occupancy also matter.

The snapshots record lanes, positions, speeds, waiting times, routes, leaders, outgoing links and upcoming signals at299,300,899,900,901,960,1200,1800 and2400s. These sparse observations characterize persistence, not a complete causal history. They must not be used to claim a general deadlock theorem or model safety.

## Next controlled diagnostic

Test whether refreshing SUMO vehicle lane-choice information after permission restoration changes the selected cases, while preserving routes and seeds. Before implementation, verify the exact SUMO API semantics. Record lane-choice state and internal-junction blockers around reopening. Keep the unmodified runs as controls, report any unsuccessful cases, and distinguish a simulator integration correction from a traffic policy. Do not use vehicle removal, teleportation or favorable-seed filtering to conceal unfinished trips. Braking still needs affected-block controls. Only then revise the protocol and rerun all development blocks.

## Verification and limitations

Independent analysis checks equality with prior summary and decisions, exact permission restoration, trip counts and decimal emissions, and snapshot population against unfinished counts. Existing38 tests pass. No paid calls. Initial instrumentation attempt v1 failed at time0 due to a snapshot indentation error before saved permissions were initialized; failed code/output are preserved, and the corrected run is separate v2. No findings use the failed attempt.
