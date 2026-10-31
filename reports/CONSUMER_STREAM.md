# Received-evidence safeguards with simulator incident truth

Development fixture, not an auditor effectiveness experiment. A SUMO component network executes a lane-permission closure at22s and reopening at38s, with0.1s steps. A focal vehicle departs at20s; the recording checks that it never enters the closed lane. Road-state observations are sampled every5s. Two previously aligned LTE parking-lot profiles transport repeated snapshots at native recorded timing, with five-second maximum observation age. The trace segment ends at55s of offset; no trace extrapolation or new radio data is used.

The common consumer adapter receives only delivered observations plus vehicle decision-point availability. Simulator road truth is evaluated separately. All policies withhold advice when evidence is unavailable and check executable route availability against received evidence. Rules/template and deadline fallback use current observations; content decisions also require a matching audited observation version. Audit verdicts are fixed accept controls, not model outputs. Deadline fallback is explicitly selected for this fixture, not a latency-prediction validation. Rejected advice produces no new route instruction.

At21s, the audit captures the20s open-road observation. The six consumption probes are21.5,22.2,25.0001,25.6,27 and50s. Four paths and two profiles give48 shadow decisions. No admitted advice is executed; traffic follows its original route and simulator lane permissions. Hence these decisions do not estimate travel effects.

-21.5s: all four paths admit while the road remains open.
-22.2s: all four paths admit from the still-fresh20s open-road observation, although the road closed at22s. Eight admissions across the two profiles are retained; they are repeated checks of one constructed event, not an error-rate estimate.
-25.0001s: the old observation has expired and the new one has not arrived; every path withholds advice.
-25.6/27s: the closure observation has arrived; every path rejects the observed unavailable route.
-50s: the advisory is expired and rejected.

The first closure observation is at25s, so source sampling itself contributes3s of invisibility before transport. Version and age gates cannot reveal an unseen event; an observation passing its age limit is not necessarily factually current. This is a limitation of shared evidence, not evidence that a particular language model failed. Event-triggered updates and sampling cadence should be separate, predeclared sensitivity conditions.

33 tests pass, covering common fallback, same-state/new-version audit invalidation, observed route closure, and unseen-change limitations. Independent verification reconciles SUMO permissions, observation timestamps, all48 decisions and zero closed-lane entries. No model calls, wall-clock inference measurement or paid usage. Earlier pilot policies remain unchanged; the new adapter is in src/v2x/consumer.py.

Next: integrate this adapter with live asynchronous audit results and realistic city lane-feasibility safeguards, then compare observation schedules and held-out incident families under an explicit frozen protocol. Source clock, trace transfer and urban calibration limitations remain.
