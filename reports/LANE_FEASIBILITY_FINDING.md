# Lane feasibility is a required preflight check

A static audit of each route propagates reachable passenger lanes across connections and permitted left/right lane changes. It checks destination-lane and internal-connection permissions. It permits unlimited lane-changing distance, making it a necessary but not sufficient test: failure establishes no legal lane sequence under the imported restrictions; success does not guarantee enough distance or traffic clearance.

Results: 19 of 600 routed requests fail this check in both the original and no-ramp imports. With lane-specific OSM access enabled, 19 of 596 routed requests fail. The failed vehicle-ID sets exactly match all 19 vehicles remaining at 2400 s in separately observed no-ramp and lane-access runs. This independently connects the persistent queues with lane-level infeasibility rather than an insufficient horizon.

Original routing validated edge sequences but did not establish this stronger lane-level property. The finding does not justify deleting these requests from the reported denominator. The original import additionally has short-connector lane exchange problems and queues behind blocked vehicles.

A candidate importing OSM lane-specific access (previously omitted) and disabling inferred ramps yields 577 arrivals, 19 running and 4 unroutable from the same 600 requests; no collisions or teleports. It is not adopted as a calibrated replacement. The earlier no-ramp run also records an emergency stop/braking warning, which must remain in safety diagnostics even though collision/teleport counts are zero.

Before freezing city experiments: define passenger demand on a validated legal lane graph, retain and report rejected requests, and validate dynamic clearance with multiple development seeds. This must be a preflight rule applied independently of auditor outcomes, not selective removal of unfavorable trips. Physical turn/access validation and communication-trace integration remain outstanding.

Evidence: reports/lane_route_audit.json; scripts/audit_route_lanes.py; runs/no_ramp_lane_inspection_v1; runs/lane_access_inspection_v1; runs/pedralbes_lane_access_v1. No inference calls or paid usage. Previous manuscript versions unchanged.
