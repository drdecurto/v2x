# V2X route guidance governance

Trustworthy LLM Route Guidance for Connected Vehicles.

The benchmark separates supported route actions, untrusted guidance wording and validity at delivery. It compares immediate templates, content auditing and timeout fallback using SUMO scenarios in Los Angeles, Luxembourg and Barcelona Pedralbes. Results are exploratory. The finite stationary LTE traces do not validate a 5G/6G stack, calibrated municipal traffic or a general emissions benefit.

Terminology: the manuscript uses *guidance message* for the delivered advice record; the underlying code and saved experiment records retain the original field name `advisory` (for example `runs/advisory_benchmark_v1`, `scripts/run_advisory_benchmark.py`). The mapping is one-to-one.

## What is included

- `src/v2x/`: runtime gates, trace alignment, incident and route consumers; the credential **loader** contains no credential.
- `scripts/`, `tests/`: experiment, verification, analysis and visualization code.
- `runs/`: saved plans, constructed cases, aggregate summaries and verification reports. A summary can contain one aggregate row per simulation run; raw trajectories, per-request logs and per-block output directories are excluded.
- `scenarios/three_city_v1/`: portable geographic development scenarios and OSM attribution. These are development scenarios; final city runs use the separately included `runs/city_preflight_v1/*/city.net.xml` networks.
- `data/derived/`: network geometry and constructed development messages, **not** SEE-V2X packet records.
- `reports/`, `protocols/`: scientific methods, provenance and limitations.
- `human_review/v1/`: blank forms only. No independent human labels are claimed.

Credentials, API billing/reservation ledgers, raw and derived packet traces, raw model responses, caches, virtual environments, downloaded third-party sources and all manuscript folders are excluded. The submission manuscript `v37_2` was not modified or included.

## Install and test

Python 3.11 or later is required; SUMO interfaces are pinned to 1.27.1.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e . pytest
.venv/bin/python -m pytest -q
```

`requirements.lock.txt` records the original environment, including optional tooling; the smaller project dependencies in `pyproject.toml` are sufficient for core tests and aggregate analysis. GUI capture requires a functioning SUMO GUI/display.

## Reproduce released aggregate analysis (offline)

```sh
.venv/bin/python scripts/reproduce_aggregate_results.py
```

This recomputes paired city means and percentile intervals using the released aggregate rows; it makes no model calls. Outputs go to ignored `outputs/`. Recorded verification JSON reports historical checks against the original full local evidence. It does not mean that all raw-data verification can be repeated from this reduced release. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Obtain the excluded radio traces

Source: [SEE-V2X project](https://cisl.ucr.edu/SEE-V2X/), DOI [10.1145/3715014.3722077](https://doi.org/10.1145/3715014.3722077).

```sh
.venv/bin/python scripts/fetch_traces.py
# Download the outdoor parking-lot archive from the official portal, then:
.venv/bin/python scripts/fetch_traces.py --archive /path/to/outdoor_parkinglot.tar.gz
.venv/bin/python scripts/prepare_traces.py
```

Alternatively use `--url` with a current direct HTTPS archive link obtained from that portal. The script verifies the exact SHA-256 before safe extraction. It rejects a changed archive rather than silently accepting different data. `data/trace_manifest.json` contains the archive and derived-file hashes. Access and redistribution remain subject to the source's terms; neither raw traces nor aligned packet-level derivatives are bundled here.

## Model-backed experiments

Local scripts use an independently installed Ollama server. Remote scripts require your own Nebius credentials, supplied as environment variables or an ignored local `credentials/nebius.env`. `.env.example` lists names only and is not loaded automatically. **No remote experiment runs during installation, testing or aggregate analysis.** Review model availability, local budget caps and the run plan before explicitly starting paid calls. Historical freeze manifests and completed result folders must not be overwritten; create a separate experiment output directory when adapting runners for a new study.

## Scope and attribution

The four-policy city comparison uses cached semantic decisions and measured service durations replayed at request time, not live per-vehicle queueing. The fifth replacement policy is a service-time replay only. Independent human label review has not been performed. Unfavorable effects, incomplete trips and safety counters are retained.

OpenStreetMap-derived networks carry ODbL obligations; see [NOTICE.md](NOTICE.md). The original study code is released under the MIT License; see [LICENSE](LICENSE). The code license does not extend to third-party data: OpenStreetMap-derived content retains its ODbL obligations, and SEE-V2X traces remain subject to the source's terms.
