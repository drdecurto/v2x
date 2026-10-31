"""Recompute all block denominators and endpoint-safe selection from XML."""
from collections import Counter
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
import sumolib
from v2x.credentials import ROOT
O=ROOT/'runs/replication_incidents_v1';S=ROOT/'runs/replication_cohorts_v1';rows=json.loads((O/'summary.json').read_text());assert len(rows)==60;checks=[]
for city in ['los_angeles','luxembourg','pedralbes']:
 net=sumolib.net.readNet(str(ROOT/'runs/city_preflight_v1'/city/'city.net.xml'),withInternal=True)
 for r in [x for x in rows if x['city']==city]:
  p=S/city/str(r['seed']);rp=p/'accepted.xml';assert hashlib.sha256(rp.read_bytes()).hexdigest()==r['input_sha256'];vs=E.parse(rp).getroot().findall('vehicle');routes={v.get('id'):v.find('route').get('edges').split() for v in vs};depart={v.get('id'):float(v.get('depart')) for v in vs};endpoints={e for route in routes.values() for e in [route[0],route[-1]]};counts=Counter(e for route in routes.values() for e in set(route[1:-1]));expected=min((e for e in counts if e not in endpoints and net.getEdge(e).getLength()>=60),key=lambda e:(-counts[e],e));assert expected==r['edge']
  requested={v.get('id') for v in E.parse(p/'trips.xml').getroot().findall('trip')};routed={v.get('id') for v in E.parse(p/'routed.xml').getroot().findall('vehicle')};assert len(requested)==600 and len(requested-routed)==r['unroutable'];assert len(routed-set(routes))==r['lane_excluded'];assert r['accepted']==len(routes)
  exposed={i for i,route in routes.items() if 310<=depart[i]<370 and expected in route};ids={x['id'] for x in r['cohort']};bad={x['vehicle'] for x in r['alternative_lane_failures']};assert exposed==ids|set(r['no_alternative'])|bad and len(ids)==r['eligible']
  for x in r['cohort']:
   i=x['id'];assert x['depart']==depart[i];assert x['route'][0]==routes[i][0] and x['route'][-1]==routes[i][-1] and expected not in x['route'];u=int.from_bytes(hashlib.sha256(f"{r['seed']}:{city}:{i}".encode()).digest()[:8],'big')/2**64;assert x['draw']==u
  for q in [.25,.5,1]:assert sum(x['draw']<q for x in r['cohort'])==r['assigned'][str(q)]
  checks.append(dict(city=city,seed=r['seed'],passed=True))
(O/'verification.json').write_text(json.dumps(dict(passed=True,blocks=len(checks),requested=sum(r['requested'] for r in rows),eligible=sum(r['eligible'] for r in rows),checks=checks),indent=2));print('Verified60 blocks, all36000 requests, deterministic edge selection, full cohort accounting and draws.')
