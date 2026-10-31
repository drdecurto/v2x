"""Independent saved-record checks for the paced asynchronous bridge."""
import json,math
from v2x.credentials import ROOT
r=json.loads((ROOT/'reports/async_validation.json').read_text())
checks=[]
for row in r['episodes']:
 p=ROOT/'runs/async_validation_v1'/row['mode'];audit=json.loads((p/'audit.json').read_text());samples=json.loads((p/'samples.json').read_text())
 paced=[x for x in samples if x['phase']=='paced'];pending=[x for x in paced if x['pending']]
 assert len(paced)==200 and pending
 assert all(b['sim_s']>a['sim_s'] and b['wall_s']>=a['wall_s'] for a,b in zip(samples,samples[1:]))
 assert row['decision_sim_s']<=40
 assert abs(row['service_s']-(audit['finished_wall']-audit['started_wall']))<1e-9
 assert row['decision_wall_s']>=audit['elapsed_s']+row['submit_wall_s']-1e-6
 assert abs(max(x['wall_s']-x['sim_s'] for x in paced)-row['max_pacing_lag_s'])<1e-8
 assert row['arrived']
 if row['mode']=='fixed_9s':
  assert any(x['sim_s']>=14 for x in pending)
  assert row['freshness_reason']=='evidence_version_changed' and not row['acted']
 if row['mode']=='fixed_2s':assert row['acted'] and row['decision_sim_s']<12
 checks.append({'mode':row['mode'],'paced_steps':len(paced),'pending_samples':len(pending),'decision_sim_s':row['decision_sim_s'],'service_s':row['service_s'],'max_pacing_lag_s':row['max_pacing_lag_s'],'arrived':row['arrived']})
ledger=[json.loads(x) for x in (ROOT/'runs/api_reservations.jsonl').read_text().splitlines()]
assert len(ledger)==72
result={'passed':True,'checks':checks,'remote_requests':72,'reserved_usd':sum(x['reserved_usd'] for x in ledger),'note':'A single local inference observation is not a latency distribution or effectiveness estimate.'}
(ROOT/'reports/async_validation_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
