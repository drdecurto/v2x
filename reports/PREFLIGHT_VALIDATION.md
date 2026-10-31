# Prospective lane preflight: three development seeds

The plan in runs/preflight_validation_v1/plan.json was written before new runs. The network is the no-ramp, lane-access import candidate, not a calibrated municipal reconstruction. Seeds 4101, 4102 and 4103 each generate 600 original-domain origin-destination requests with fixed demand parameters. Seed 4101 is prior development evidence, while 4102/4103 are additional development checks, not held-out confirmation. There is no replacement sampling to conceal rejected requests.

| Seed | Requested | Unroutable | Lane-infeasible | Accepted and arrived | Accepted unfinished |
|---|---:|---:|---:|---:|---:|
| 4101 | 600 | 4 | 19 | 577 | 0 |
| 4102 | 600 | 7 | 17 | 576 | 0 |
| 4103 | 600 | 1 | 26 | 573 | 0 |
| Total | 1800 | 12 | 62 | 1726 | 0 |

Acceptance is computed from route connectivity, passenger permissions and legal lane changes before simulation outcomes. All accepted departures and routes exactly equal their original routed records; only preflight-failing requests are absent from the filtered traffic. Every rejected ID and reason is recorded. Static feasibility is necessary, not sufficient, because it assumes enough lane-changing distance and does not model dynamic conflicts.

Separate unfiltered runs have exactly 19,17,26 unfinished vehicle IDs, matching the respective preflight rejection sets. The 4101 unfiltered measurement is reused after checking exact route/departure equality; no duplicate job. All accepted requests clear by 2400 s without teleportation or behavioral override. There are no recorded collisions or teleports. The unfiltered 4103 run records one emergency-braking event; filtered runs record none. These are development diagnostics, not safety evidence.

The full-request arrival total remains 1726/1800 (95.89%): preflight does not increase the number served. Conditional accepted-demand clearance is 1726/1726 and must always be accompanied by the 74 rejected requests. Removing traffic changes interactions, so filtered/unfiltered contrasts cannot estimate an auditor's benefit or a causal control effect. No calibration claim follows from these three seeds.

Independent checks in scripts/verify_preflight.py reconcile IDs and all requests, verify unchanged routes/departures, compare rejected IDs to unfinished trips, and check exact agreement of reused baseline routes. Twelve existing unit tests pass. Original networks, runs and manuscript versions remain unchanged.

Next: apply preflight consistently to all city configurations, preserve requested/accepted demand coverage, and integrate chronological observation transport with empirical traces. Freeze the final network, demand rule and held-out templates/seeds before policy outcomes. Continue physical map/signal/access validation; these checks do not establish observed traffic realism.
