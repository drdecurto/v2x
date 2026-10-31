import json
from pathlib import Path
import pandas as pd
from v2x.credentials import ROOT
O=ROOT/'runs/chronological_replay_v1';checks=[]
for summary in json.loads((O/'summary.json').read_text()):
 i=summary['profile'];packets=pd.read_csv(ROOT/f'data/derived/see_parkinglot_{i}.csv').to_dict('records');e=[json.loads(x) for x in (O/str(i)/'emissions.jsonl').read_text().splitlines()];r=[json.loads(x) for x in (O/str(i)/'deliveries.jsonl').read_text().splitlines()]
 assert len(e)==len(packets)
 for a,b in zip(e,packets):
  assert a['source_seq']==b['seq'] and a['received']==b['received'] and abs(a['tx_s']-5-b['tx_offset_s'])<1e-10
  assert a['observed_at_s']<=a['tx_s'] and a['tx_s']-a['observed_at_s']<5
  if b['received']:assert abs(a['rx_s']-a['tx_s']-b['delay_s'])<1e-10
 assert {x['packet_index'] for x in r}=={x['packet_index'] for x in e if x['received']}
 version=-1;last_time=-1
 for x in r:
  assert x['rx_s']>=last_time;last_time=x['rx_s']
  if x['decision']=='updated':assert x['observation_sequence']>version and x['age_s']<=5;version=x['observation_sequence']
  elif x['decision']=='age_rejected':assert x['age_s']>5
  elif x['decision']=='duplicate':assert x['observation_sequence']==version
  elif x['decision']=='superseded_rejected':assert x['observation_sequence']<version
  else:raise AssertionError('unknown decision')
 checks.append({'profile':i,'native_tx_loss_delay_preserved':True,'causal_snapshot_selection':True,'all_and_only_recorded_arrivals':True,'monotone_receiver_versions':True,'received':len(r)})
(O/'checks.json').write_text(json.dumps(checks,indent=2));print(checks)
