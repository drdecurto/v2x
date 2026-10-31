"""Independent route/assignment/accounting checks for development uptake runs."""
import hashlib,json,xml.etree.ElementTree as E
from decimal import Decimal
from v2x.credentials import ROOT
O=ROOT/'runs/city_uptake_v3';checks=[]
for city in ['los_angeles','luxembourg','pedralbes']:
 fx=json.loads((O/city/'fixture.json').read_text());original={v.get('id'):v.find('route').get('edges').split() for v in E.parse(ROOT/'runs/city_preflight_v1'/city/'accepted.xml').getroot().findall('vehicle')};previous=set()
 for f in [0,.25,.5,1]:
  p=O/city/str(f);r=json.loads((p/'result.json').read_text());a=json.loads((p/'assignment.json').read_text());expected={i for i in original if int.from_bytes(hashlib.sha256(f'4101:{city}:{i}'.encode()).digest()[:8],'big')<f*2**64};assert expected==set(a['assigned']) and previous<=expected;previous=expected
  selected=expected&set(fx['eligible_alternatives']);assert selected==set(a['diverted'])
  routes={v.get('id'):v.find('route').get('edges').split() for v in E.parse(p/'routes.xml').getroot().findall('vehicle')};assert set(routes)==set(original)
  for ident,route in routes.items():
   assert route==(fx['eligible_alternatives'][ident] if ident in selected else original[ident])
   if ident in selected:assert fx['edge'] not in route and route[0]==original[ident][0] and route[-1]==original[ident][-1]
  trips=list(E.parse(p/'tripinfo.xml').getroot());assert len({t.get('id') for t in trips})==len(trips)
  total=sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/1000000
  assert abs(total-Decimal(str(r['co2_kg'])))<Decimal('.00000001')
  assert r['arrived']+r['running']+r['pending']+r['excluded']==600 and r['closed_edge_occupancy_samples']==0
  checks.append(dict(city=city,uptake=f,assignments_verified=len(expected),routes_verified=len(routes),co2_verified=True,passed=True))
(O/'verification.json').write_text(json.dumps(checks,indent=2));print('Verified',len(checks),'episodes')
