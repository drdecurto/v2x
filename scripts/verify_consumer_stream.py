import json
from pathlib import Path
from v2x.credentials import ROOT
O=ROOT/'runs/consumer_stream_v1';truth=json.loads((O/'truth.json').read_text());obs=json.loads((O/'observations.json').read_text());rows=json.loads((O/'decisions.json').read_text())
assert len(rows)==48
assert all(x['closed']==(22<=x['t']<38) for x in truth)
assert all(x['road']!='main' for x in truth if x['closed'])
assert next(x for x in obs if x['observed_at_s']==20)['road_A_closed'] is False
assert next(x for x in obs if x['observed_at_s']==25)['road_A_closed'] is True
for row in rows:
 t=row['time_s'];mode=row['decision']['mode']
 if t==22.2:assert row['decision']['admit'] and row['true_closed'] and row['received_sequence']==4
 if t==25.0001:assert mode=='evidence_unavailable' and not row['decision']['admit']
 if t in [25.6,27]:assert mode=='observed_route_unavailable' and not row['decision']['admit']
 if t==50:assert mode=='invalid_or_expired'
assert sum(x['admitted_closed_road_advisory'] for x in rows)==8
report={'passed':True,'shadow_checks':48,'hidden_change_admissions':8,'closed_lane_entries':0,'sampling_delay_s':3,'note':'Same constructed event across four paths and two trace profiles; not48 independent trials or model measurements.'}
(O/'checks.json').write_text(json.dumps(report,indent=2));print(report)
