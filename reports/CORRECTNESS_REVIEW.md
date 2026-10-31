# V2X correctness review

## Conclusion
The saved development measurements reconcile, but the three-city benchmark is not yet ready for confirmatory effectiveness comparisons. Pedralbes has verified lane/route incompatibilities at three persistent queue heads. No traffic repair has been applied in this review.

## Checks passed
- All 1800 requested city trips are accounted for, including unfinished and uninserted vehicles. LA and Luxembourg each finish 600; Pedralbes finishes 532, with 66 still running and 2 pending.
- Network hashes, detector lane placement, source record counts and sequence order agree with the saved evidence. Publication colors do not change map geometry.
- All 12 component unit tests pass. The 12 closure diagnostics and their eight descriptive means reconcile; the three asynchronous episodes preserve movement while inference is pending and correctly gate superseded evidence.
- Paid-call ledger remains at 72 reservations and USD 1.046466 conservative accounting. This review made no model calls.

## Blocking correctness finding: Pedralbes
A separate unchanged-scenario run adds lane connectivity and best-lane observations. Independently cross-checking those observations against the network XML establishes:
1. Vehicle 4 stops on Avinguda Diagonal lane 1391890990#0_0. That lane has no outgoing connections. Its required next edge cannot be reached directly from the current lane.
2. Vehicles 107 and 126 stop in opposite lanes on the 7.81 m Carrer de Can Caralleu segment 975794527#0. Each vehicle's required continuation is connected from the other lane. Neither has a scheduled stop; both wait for 3357 seconds.
3. The reported green next traffic light is not sufficient evidence of an executable movement from the vehicle's current lane. A route-level signal query must not replace lane-level connectivity checks.

This identifies immediate blocking conditions, not yet the full cause of poor lane selection or a physically justified repair. Do not fix this by teleporting vehicles, adding arbitrary turns, or excluding incomplete trips. Inspect upstream lane assignment and imported junction/turn geometry, then compare a justified repair with the unchanged scenario using identical demand. More seeds and independent calibration will still be required.

## Manuscript assessment
V8 correctly presents the results as development checks and explicitly flags persistent Pedralbes queues. Its counts remain valid; the diagnosis is now more specific. No effectiveness, safety, real-city calibration or 5G/6G validation claim is supported by these checks. The E2 halting and current-presence fields should remain separate rather than forming a ratio. LA and Luxembourg trip completion alone does not validate their signal plans.

## Evidence
runs/pedralbes_lane_diagnostic_v1/snapshots.json and queue_head_checks.json; scripts/verify_pedralbes_queue_heads.py; reports/three_city_checks.json; reports/async_validation_checks.json. Original v7/v8 packages and raw results remain unchanged. This review is an additional diagnostic of the same seed, not an independent experimental replication.
