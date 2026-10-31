# Three-city roadside infrastructure: implemented scope

The imported OpenStreetMap road networks represent bounded areas of downtown Los Angeles, central Luxembourg City and Barcelona's Pedralbes area. Buildings and land use are map-derived. Passenger-only traffic, random OD demand, missing lane/speed inference and generated actuated signal plans are experimental assumptions, not reconstructions of actual municipal operation. Public transport, pedestrians and cyclists are not yet simulated.

## Implemented
- Up to 12 existing imported signal controllers per city are instrumented. Selection ranks incoming lanes by generated development-route use, with deterministic ID tie-breaking. This is development placement, not an optimized deployment or held-out selection.
- E2 lane-area detectors cover up to the last 80 m of each passenger approach lane at these intersections. They expose vehicle count, halting count and occupancy. Ideal simulator measurements have no camera errors or weather effects yet.
- Orange POIs mark hypothetical roadside units (RSUs). Every 5 simulated seconds, each RSU exports a versioned, timestamped record of detector readings, current signal state and the presently scheduled switch time. Adaptive signals can change that time; it is explicitly a prediction, not guaranteed time-to-green.
- SUMO's built-in actuated controllers respond to their own automatic detector inputs. Added E2 sensors supply advisory evidence; they are not represented as controlling those signals. Imported warning logs are retained for controller calibration.
- Network truth is retained separately from future delivered observations. The present test records source observations only; radio replay, message delivery and auditor decisions are not yet coupled to these city runs.

## Planned paired comparisons
Use identical traffic realizations for no roadside observations versus delivered roadside observations, then fresh versus delayed/lost readings. Separately compare fixed-time and actuated signal control; do not change control policy between auditor conditions. Estimate queues and route usefulness from received evidence, never future simulator state. Include stale queue claims, misleading closure text and uncertain signal predictions. LLMs assess text and do not directly command signals.

## Protocol boundary and sources
The JSON observation record is an experimental application interface. Signal-state and map-geometry information are useful for a future SPaT/MAP-like interface, but no SAE J2735 encoding, ETSI interoperability, radio coverage or security certification is implemented. An orange RSU marker does not establish a measured wireless link. Existing LTE trace evidence must retain its original technology label.

- SUMO OSM import: https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- SUMO actuated traffic signals: https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html
- SUMO E2 detectors: https://sumo.dlr.de/docs/Simulation/Output/Lanearea_Detectors_(E2).html
- Map attribution: © OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright

Do not infer effectiveness from a single seed or compare these equal trip counts as calibrated city congestion levels. Freeze sampling, network edits, demand scaling and observation faults before confirmatory runs.

## Diagnostic limitations retained
Fourteen E2 samples have halting count above simultaneous vehicle count (5 LA, 2 Luxembourg, 7 Pedralbes). Do not assume these API fields share an instantaneous counting denominator; reconcile detector semantics before deriving proportions. Signal warning counts are 14, 3 and 6. Pedralbes has 68 uncompleted requests at cutoff, including two not inserted. Failed unsorted-tile import attempts remain separate and are excluded.
