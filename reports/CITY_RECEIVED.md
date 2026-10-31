# Finite stationary-trace city routing integration

Development only: three deterministic-template runs, seed4101, closure0–900s, horizon2400s, same preflighted city routes and 50% driver draws. No inference calls or policy-effect estimate. All source observations come from current SUMO lane permission state; the consumer receives only transported observations. Alternative availability means a saved preflighted route avoiding the sole closure, not an online traffic optimum.

One stationary LTE profile6 is replayed once per city at native timing:4949transmissions,3431receipts. Arrival processing is quantized to the next0.5s step. The link is shared by all clients, rather than independent spatial channels. Freshness expires5s after observation; trace exhaustion deliberately leaves later decisions unavailable. One decision per exposed driver with a valid alternative, on actual departure while on the original first edge; no retry.

Applied detours:LA6,Luxembourg4,Pedralbes8. Evidence unavailable:56/66,105/116,72/81. All600/600/577accepted trips arrive, with23Pedralbes exclusions retained. CO2kg:652.51980888,488.87641579,494.42909197. No closed-edge occupancy, collisions, emergency braking/stops or teleports. Original actuated detector-coverage warnings persist.

Independent verification reconciles every native packet timing/loss record, all263decisions, applied route identity, source freshness and decimal-summed trip-device CO2.38tests pass. Raw packet-derived logs remain local pending trace redistribution clearance; manuscript package includes only aggregates, simulator evidence and code. No new model calls; reservations remain72/USD1.046466.

Next: define a workload/trace window alignment that exposes useful decisions without looping or extending measured traces, before outcomes; compare common policies with measured inference and declared selection deadlines. Do not tune trace alignment using these emissions. Validate outdoor mobility traces and freeze held-out families, samples and analysis before confirmation.
