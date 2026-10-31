import json,hashlib,xml.etree.ElementTree as E
from pathlib import Path
import sumolib
from v2x.credentials import ROOT
checks=[]
for city in ['los_angeles','luxembourg','pedralbes']:
 p=ROOT/'runs/city_infrastructure_v2'/city;r=json.loads((p/'validation.json').read_text());infra=json.loads((p/'infrastructure.json').read_text())
 d=ROOT/'data/derived'/city;net=d/('downtown.net.xml' if city=='los_angeles' else 'city.net.xml');n=sumolib.net.readNet(str(net))
 assert hashlib.sha256(net.read_bytes()).hexdigest()==r['net_sha256']
 assert len(n.getEdges())==r['edges']
 trips=list(E.parse(p/'tripinfo.xml').getroot());stats=E.parse(p/'statistics.xml').getroot();v=stats.find('vehicles')
 arrived=sum(float(t.get('arrival',-1))>=0 for t in trips);running=int(v.get('running'));waiting=int(v.get('waiting'));loaded=int(v.get('loaded'))
 assert arrived==r['arrived'] and arrived+running+waiting==loaded
 observations=[json.loads(x) for x in (p/'observations.jsonl').read_text().splitlines()]
 assert len(observations)==r['observation_records']
 previous={}
 for o in observations:
  assert o['observed_at_s']>previous.get(o['source_id'],0);previous[o['source_id']]=o['observed_at_s']
  assert o['sequence']*5==o['observed_at_s']
  assert o['scheduled_switch_s']>=o['observed_at_s']
  for s in o['detectors']:assert s['halting']>=0 and s['vehicles']>=0 and 0<=s['occupancy_pct']<=100
 for s in infra['sensors']:assert n.getLane(s['lane']).allows('passenger') and s['length_m']>0
 a=E.parse(d/'buildings.poly.xml').getroot();b=E.parse(d/'publication.poly.xml').getroot()
 assert len(a)==len(b)
 for x,y in zip(a,b):assert {k:v for k,v in x.attrib.items() if k!='color'}=={k:v for k,v in y.attrib.items() if k!='color'}
 checks.append({'city':city,'passed':True,'arrived':arrived,'running':running,'waiting_to_insert':waiting,'loaded':loaded,'detectors':len(infra['sensors']),'record_count':len(observations),'halting_exceeds_vehicle_count_samples':sum(s['halting']>s['vehicles'] for o in observations for s in o['detectors']),'warnings':sum('Warning:' in line for line in (p/'errors.log').read_text().splitlines())})
(ROOT/'reports/three_city_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
