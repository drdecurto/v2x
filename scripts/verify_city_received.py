"""Independent reconciliation of native arrivals, causal choices and SUMO output."""
import json,xml.etree.ElementTree as E,math
from decimal import Decimal
import pandas as pd
from v2x.credentials import ROOT
O=ROOT/'runs/city_received_v1';packets=pd.read_csv(ROOT/'data/derived/see_parkinglot_6.csv').to_dict('records');checks=[]
for city in ['los_angeles','luxembourg','pedralbes']:
 p=O/city;r=json.loads((p/'result.json').read_text());obs=json.loads((p/'observations.json').read_text());sent=json.loads((p/'sent.json').read_text());deliveries=json.loads((p/'deliveries.json').read_text());decisions=json.loads((p/'decisions.json').read_text());fx=json.loads((ROOT/'runs/city_uptake_v3'/city/'fixture.json').read_text())
 assert len(sent)==len(packets)
 for x in sent:
  q=packets[x['index']];assert x['received']==bool(q['received']) and x['tx_s']==q['tx_offset_s'];assert x['sequence']==int(x['tx_s']//5)
 expected=[]
 for i,q in enumerate(packets):
  if q['received']:
   rx=q['tx_offset_s']+q['delay_s'];expected.append((rx,i,math.ceil(rx/.5)*.5))
 expected.sort();assert len(expected)==len(deliveries)
 for (rx,i,step),d in zip(expected,deliveries):assert d['index']==i and abs(d['rx_s']-rx)<1e-8 and abs(d['processed_s']-step)<1e-8
 for d in decisions:
  t=d['time_s'];available=[x for x in deliveries if x['processed_s']<=t and x['status']=='updated'];latest=obs[available[-1]['sequence']] if available else None
  if latest is not None and t-latest['observed_at_s']>5:latest=None
  assert d['evidence']==latest
  ident=d['result']['vehicle_id']
  if d['route_applied']:
   assert latest and latest['road_A_closed'] and fx['draws'][ident]<.5
   assert d['route_after']==fx['eligible_alternatives'][ident] and fx['edge'] not in d['route_after']
  if latest is None:assert not d['route_applied']
 trips=list(E.parse(p/'tripinfo.xml').getroot());total=sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/1000000
 assert abs(total-Decimal(str(r['co2_kg'])))<Decimal('.00000001')
 assert r['arrived']+r['running']+r['pending']+r['excluded']==600 and r['closed_edge_occupancy_samples']==0
 checks.append(dict(city=city,packet_records=len(sent),received=len(deliveries),decision_records=len(decisions),co2_kg=str(total),passed=True))
(O/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
