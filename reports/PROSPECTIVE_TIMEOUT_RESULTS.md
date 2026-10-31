# Prospective timeout results

32 actual local calls on16cases per model, all parseable; plan and runner hashes fixed before inference.12new-wording stable cases plus4synthetic temporal cases per model. Existing38 tests pass; independent verification passes. No paid calls.

| Model | Clean content actions /3 | Clean timeout actions /3 | Violating original texts: none/templates/content/timeout (out of6) | Maximum timeout decision s |
|---|---:|---:|---|---:|
| Llama3.1:8b |2|3|6/0/0/0|2.010|
| Phi4 |0|3|6/0/0/0|2.005|

Content decisions can reach5.011s, beyond both nominal5sdeadline and the unchanged observation's age limit. Suppression at that boundary is not counted as a correct semantic rejection. First requests include loading; this is not a steady-state ranking. The timer is prospective, whereas v28service_matrix remains a separate retrospective oracle experiment. Immediate templates retain all3clean actions and deliver no violating original text too; no added integrity benefit over that baseline is established.

Temporal tests verify that fallback does not bypass stale evidence, expiry or a passed choice point. Superseded audit results are blocked; fallback may legitimately render the newer observation when available. All decisions are committed before draining late responses. One actual inference future is shared by paired observers; no separate-server capacity, request cancellation or energy saving is claimed. Model responses are judged against constructed references, and unsure-prediction boundaries lack independent human validation.

Main manuscript v29 adds the concise prospective evidence while retaining city failures. This is meaningful implementation progress, not a completed city-effectiveness study. Next: strengthen independent ground-truth/uncertainty validation and non-oracle asynchronous service tests with finite trace delivery; keep the scope honest if full traffic integration cannot be resolved before the deadline.
