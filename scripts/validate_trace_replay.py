import json,hashlib,fcntl
from collections import Counter
from pathlib import Path
import pandas as pd
from v2x.credentials import ROOT
from v2x.replay import replay_observations
O=ROOT/'runs/chronological_replay_v1';O.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'reports/trace_manifest.json').read_text())
plan={'profiles':[1,6],'source':'runs/city_infrastructure_v2/los_angeles/observations.jsonl','source_id':'RSU_0','epoch_s':5,'max_observation_age_s':5,'mode':'one redundant source snapshot per recorded packet, original TX timing and loss; latest causal 5s sensor record; drain all recorded arrivals','scope':'offline single-link stationary LTE trace sensitivity; not urban radio calibration, no audit/traffic feedback or new field measurements'}
if not (O/'plan.json').exists():(O/'plan.json').write_text(json.dumps(plan,indent=2))
with (O/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (O/'summary.json').exists():raise SystemExit('Completed; no duplicate replay')
 observations=[o for line in (ROOT/plan['source']).open() if (o:=json.loads(line))['source_id']==plan['source_id']]
 summaries=[]
 for profile in plan['profiles']:
  src=ROOT/f'data/derived/see_parkinglot_{profile}.csv';m=next(x for x in manifest['traces'] if x['configuration']['id']==profile)
  assert hashlib.sha256(src.read_bytes()).hexdigest()==m['derived_sha256']
  packets=pd.read_csv(src).to_dict('records');e,r=replay_observations(packets,observations,epoch_s=5,max_age_s=5)
  p=O/str(profile);p.mkdir(exist_ok=True)
  for name,items in [('emissions',e),('deliveries',r)]:
   with (p/(name+'.jsonl')).open('w') as f:
    for item in items:f.write(json.dumps(item)+'\n')
  max_burst=burst=0
  for item in e:
   burst=0 if item['received'] else burst+1;max_burst=max(max_burst,burst)
  used={x['observation_sequence'] for x in e};encoded=max(len(json.dumps(x,separators=(',',':')).encode()) for x in observations if x['sequence'] in used)
  assert encoded<=1470
  summary={'profile':profile,'packets':len(e),'received':len(r),'lost':len(e)-len(r),'max_consecutive_lost_packets':max_burst,'source_observations_used':len(used),'decisions':dict(Counter(x['decision'] for x in r)),'max_json_snapshot_bytes':encoded,'recorded_packet_size':1470,'trace_duration_s':packets[-1]['tx_offset_s'],'source_sha256':hashlib.sha256((ROOT/plan['source']).read_bytes()).hexdigest(),'trace_sha256':m['derived_sha256'],'note':'JSON byte check excludes protocol overhead and is not wire-format validation. Repeated snapshots match recorded offered load, not sparse advisory traffic.'}
  assert len(e)==m['observed_tx'] and len(r)==m['received'];summaries.append(summary)
 (O/'summary.json').write_text(json.dumps(summaries,indent=2));print(json.dumps(summaries,indent=2))
