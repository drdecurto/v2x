import json,math,xml.etree.ElementTree as E
from v2x.credentials import ROOT
O=ROOT/'runs/static_sensors_v1';rows=[]
for result in json.loads((O/'summary.json').read_text()):
 city=result['city'];p=O/city;src=ROOT/'runs/city_preflight_v1'/city
 a=E.parse(src/'city.net.xml');b=E.parse(p/'city.net.xml')
 for t in a.getroot().findall('tlLogic'):t.set('type','static')
 assert E.tostring(a.getroot())==E.tostring(b.getroot())
 accepted={v.get('id') for v in E.parse(src/'accepted.xml').getroot().findall('vehicle')}
 trips=list(E.parse(p/'tripinfo.xml').getroot());arrived={v.get('id') for v in trips if float(v.get('arrival'))>=0};unfinished={v.get('id') for v in trips if float(v.get('arrival'))<0}
 assert not arrived&unfinished and arrived|unfinished<=accepted
 assert len(arrived)==result['arrived']
 infrastructure=json.loads((p/'infrastructure.json').read_text());sensors={x['id']:x for x in infrastructure['sensors']};rsus={x['id']:x for x in infrastructure['rsus']};seen=set();positive=0;halting_exceeds=0
 for line in (p/'observations.jsonl').read_text().splitlines():
  r=json.loads(line);key=(r['source_id'],r['sequence']);assert key not in seen;seen.add(key)
  assert r['observed_at_s']==5*r['sequence'] and 1<=r['sequence']<=480
  assert r['controller']=='static' and r['tls']==rsus[r['source_id']]['tls']
  assert r['next_switch_s']>=r['observed_at_s'] and math.isfinite(r['next_switch_s'])
  expected={k for k,v in sensors.items() if v['tls']==r['tls']};assert {d['id'] for d in r['detectors']}==expected
  for d in r['detectors']:
   assert d['vehicles']>=0 and d['halting']>=0 and math.isfinite(d['occupancy_pct']) and 0<=d['occupancy_pct']<=100
   halting_exceeds+=d['halting']>d['vehicles']
  positive+=any(d['vehicles']>0 for d in r['detectors'])
 assert len(seen)==result['records']==len(rsus)*480 and positive==result['positive_records']
 warnings=[x for x in (p/'errors.log').read_text().splitlines() if 'no controlling detector' in x]
 rows.append(dict(city=city,network_only_type_changed=True,records_checked=len(seen),signal_detector_warning_lines=len(warnings),halting_exceeds_presence_records=halting_exceeds,arrived=len(arrived),passed=True))
(O/'verification.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
