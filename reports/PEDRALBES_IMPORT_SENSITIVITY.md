# Pedralbes import sensitivity: development diagnosis

Two candidates were declared in runs/pedralbes_import_sensitivity_v1/plan.json before execution. Both use the original OSM extract and the identical 600 origin-destination requests and departure times, seed 4101, 0.5 s steps and a 2400 s horizon, with teleportation disabled. Routes were recomputed on each network; these are not controlled auditor or signal-policy comparisons.

| Import | Requested | Routed | Arrived | Running | Pending insertion | Unroutable |
|---|---:|---:|---:|---:|---:|---:|
| Original, recorded v7 | 600 | 600 | 532 | 66 | 2 | 0 |
| Disable ramp guessing | 600 | 600 | 581 | 19 | 0 | 0 |
| Disable ramp guessing and all turnarounds | 600 | 556 | 556 | 0 | 0 | 44 |

All runs record zero collisions and teleports. The last candidate is not a 100% completion success: 44 requests cannot be routed. Its full-request completion is 556/600. Neither candidate is adopted as a calibrated replacement. Disabling ramp guessing also changes other inferred ramp geometry and route choices, so the first contrast does not isolate a single local defect.

## Mechanistic evidence
Original import connections force traffic from two single-lane approaches into different lanes of a 7.81 m connector. Queue-head vehicles 107 and 126 require opposite outgoing lanes. The raw OSM way 975794527 has two lanes; the original import has three after heuristic processing. A separate queue-head vehicle 4 is on lane 1391890990#0_0, which has no outgoing connection. That edge's only outgoing connection is a turnaround from lane 2. Raw OSM carries change:lanes:forward=yes|not_right|not_left on the Diagonal approach. This supports inspection of inferred topology and restricted lane access, not arbitrary removal of restrictions.

## Decision
Keep original v7/v8 data and both diagnostic candidates. No signal overrides, vehicle teleporting, arbitrary new turn links or exclusion of failed requests is used to declare success. Next inspect the remaining 19 vehicles in the no-ramp candidate and validate OSM turn/access restrictions against the import. A defensible final network and predeclared feasible-demand construction must precede held-out evaluation. Choosing the highest arrival count on this development seed is not calibration.

## Reproduction and scope
scripts/test_pedralbes_imports.py writes exclusive-lock, resumable runs with raw conversion/routing logs, trip records and statistics. Each row reconciles arrived + running + pending + unroutable = 600. No model calls; paid ledger unchanged. Primary documentation: https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html and https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html .
