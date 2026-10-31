# Finite chronological observation replay

Development plan: runs/chronological_replay_v1/plan.json, written before execution. Replays two acquired SEE-V2X stationary parking-lot LTE C-V2X profiles (IDs1 and6), both recorded at1470 bytes per packet and nominal20ms intervals, with differing source priority settings. The original chronological TX offsets, matched delivery flags and delays are retained. No shuffle, IID Bernoulli replacement, time stretching, wraparound or extrapolation is used. SHA256 hashes match the existing alignment manifest.

One hypothetical LA RSU (RSU_0) supplies the latest causally available observation every recorded transmission opportunity. Simulator observations are generated every5s; repeated transmission at the trace's offered rate provides redundancy. Epoch is5s, maximum accepted observation age5s. Every recorded arrival is processed in arrival order, including arrivals after the last transmission. Older versions cannot roll back newer received evidence. The receiver does not consult future source observations. This finite offline experiment has no active simulator feedback, model calls or real radio hardware.

| Profile | TX | Received | Lost | Longest loss run | Source updates used/delivered | Age-rejected packets |
|---|---:|---:|---:|---:|---:|---:|
|1|6270|5327|943|112|26/26|23|
|6|4949|3431|1518|115|20/20|11|

Repeated copies account for5278 and3400 received packets. All source versions are eventually delivered in these windows, but this does not establish continuous freshness or deadline success. Packet rejection is not source-update loss. Compact JSON snapshots use at most682/669 bytes, below the recorded1470-byte profile size; this excludes protocol/security overhead and is not on-air encoding validation. No claim of sparse-advisory workload calibration follows from repeated50Hz snapshots.

The original trace alignment excludes uncertain receiver logging boundaries and retains source synchronization uncertainty. Stationary LTE results are transferred as a sensitivity condition, not calibrated Los Angeles mobility, NR sidelink, 5G or6G evidence. Raw/derived trace records and packet-level replay outputs remain local pending redistribution permission; the manuscript package contains aggregate summaries, manifests and implementation only.

Verification:20 tests pass, including reordered arrival/version rollback, consecutive losses, future-evidence exclusion, exact age boundary and malformed timing. Independent checks reconcile every TX timestamp, loss flag, receive delay and packet ID against the stored trace, as well as causal source selection and monotone consumer versions.

Next: quantify time spent without sufficiently fresh evidence and couple the stream to the same evidence-only consumer used by auditing policies. Validate appropriate outdoor mobility traces and payload/transport assumptions before freezing communication conditions. Apply lane preflight consistently to city demand before any integrated policy comparison.
