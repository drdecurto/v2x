# Time-weighted receiver freshness

Development analysis of the existing finite chronological replays, not new radio measurements. The window is exactly first-to-last recorded transmission; draining later arrivals is excluded from the coverage denominator. The five-second age limit is unchanged. Unknown evidence before the first arrival counts as unavailable. Source truth is never used to advance receiver state.

| Profile | Window s | Fresh s | Stale s | Initially missing s | Fresh % | Longest unavailable s |
|---|---:|---:|---:|---:|---:|---:|
|1|125.379640|123.773925|1.586827|0.018888|98.7193|0.385830|
|6|98.960027|96.435868|2.514250|0.009909|97.4493|1.172889|

All updates eventually arrive, but stale intervals occur before some replacements. The receiver retains the last known version internally while returning no usable evidence once its age exceeds five seconds. It cannot infer unseen source changes. Receive-time and use-time checks are separate. Coverage is time-weighted, not packet-weighted. Mean known-evidence ages (including stale periods) are2.556670 and2.606486s; maxima are5.385830 and6.172889s. Missing periods have no invented numerical age.

Exact integration splits at accepted receipt times and expiry times. An independent observation-only receiver processes all original arrival events during a1ms midpoint sweep. Its fresh-duration estimates differ by5.285ms and2.841ms, below declared discretization bounds54ms and42ms. Native replay decisions match the stateful receiver exactly.26 tests pass, including an analytic integration fixture, clipping, expiry without new packets, out-of-order versions and invalid times. An initially mistyped hand-calculated expected integral was corrected from35 to35.5 square seconds; implementation matched direct integration.

This remains a stationary LTE trace sensitivity for one redundantly transmitted RSU stream, not urban channel calibration, independent replicated traffic trials or evidence of auditing effectiveness. Source packet traces and packet-level replay records stay local. Next couple this received-evidence API to common auditor/consumer safeguards with explicit fallback during missing/stale periods, and validate held-out trace selection before policy comparisons.
