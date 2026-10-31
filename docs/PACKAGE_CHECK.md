# Staging validation

- 41 tests pass: 38 original invariants plus three archive-fetch tests (checksum rejection, traversal rejection and valid layout installation).
- Offline aggregate reproduction matches all24 saved city/metric/policy mean and interval comparisons within1e-10. Uses the original Python bootstrap method and percentile order statistics.
- Scanned all publication files for exact locally configured secret values (without logging them), common credential/private-key signatures, local absolute paths and forbidden raw trace/ledger artifacts. No matches.
- No raw or aligned packet traces, model-response JSONL, private ledger, environment, caches, downloaded web source or manuscript folder included.
- Main v37_2/main.tex and main.pdf retain initial SHA-256. Some supporting metadata/QA files changed externally during staging. No operation in this packaging task writes to v37_2.
- Fetch helper tested with synthetic archives. No external archive was redownloaded and no new model call was made.
- Repository not initialized, uploaded or published. Software license remains an author decision; third-party OSM attribution retained.
