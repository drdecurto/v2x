# Pedralbes traffic and detector diagnostic

Development only; original v7 observations are unchanged. No model calls or paid usage.

## Persistent traffic
A separately logged run keeps seed 4101, all 600 routes, signal programs, step length and teleport prohibition unchanged, extends the horizon from 2400 to 3600 seconds and adds vehicle/leader/route snapshots. At 3600 s there are still 66 running vehicles and two not inserted. All 66 have waited continuously for more than 600 s. Extending the horizon alone does not repair this condition.

Queues concentrate on lanes 114608760_0 (21 vehicles), 1391890990#0_0 (17) and 288612544#0_0 (9), with additional vehicles on connecting and internal lanes. Several head vehicles report a green next signal with no same-route leader. This does not prove a signal failure: turning conflicts, lane connectivity and short-edge lane choice still require investigation. No route, signal, collision or teleport override was applied. Do not interpret this as measured congestion in Barcelona.

Evidence: runs/pedralbes_diagnostic_v1/{snapshots.json,tripinfo.xml,statistics.xml,summary.json}. This is a new diagnostic of the same deterministic scenario, not an independent replication.

## Detector semantics
The version-matched SUMO 1.27.1 source distinguishes the two counters. MSE2Collector::getCurrentVehicleNumber counts retained vehicle records whose onDetector flag is true. detectorUpdate processes movement notifications, including departed vehicles, and checkJam increments the halting counter for low-speed notifications; departing records are then removed. Thus the halting count and current presence count do not necessarily have the same denominator.

A reproduced Pedralbes sample at 250 s has detector E2_3_1 reporting zero vehicles and an empty vehicle-ID list, but one halting vehicle. The underlying lane is empty at that query. This is consistent with the source's distinct temporal supports; it is not evidence of a fabricated observation. Five discrepancies were reproduced in the first 900 s; v7's seven Pedralbes discrepancies cover the full 2400 s. Preserve raw values. Do not clamp halting counts or derive halting/vehicle proportions from these fields. Future queue features should use documented occupancy or separately defined, temporally aligned measures.

Primary sources inspected:
- https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/libsumo/LaneArea.cpp
- https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/output/MSE2Collector.cpp (detectorUpdate, checkJam, getCurrentVehicleNumber)
- https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/output/MSE2Collector.h

## Next
Inspect turning connectivity, best-lane constraints and junction blocking at the identified queue heads; preserve an unmodified comparison when testing a repair. Complete this before freezing demand or treating urban runs as policy-effectiveness evidence. Trace-driven observation transport and held-out planning remain pending.
