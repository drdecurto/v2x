"""Independent denominator reconstruction; no simulator outcomes used."""
import json,hashlib,xml.etree.ElementTree as E
from v2x.credentials import ROOT
p=ROOT/'runs/alignment_v1';plan=json.loads((p/'plan.json').read_text());out=json.loads((p/'summary.json').read_text());manifest=json.loads((p/'manifest.json').read_text())
assert hashlib.sha256((p/'plan.json').read_bytes()).hexdigest()==manifest['plan_sha256']
for name,digest in manifest['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
for r in out['cities']:
 city=r['city'];fx=json.loads((ROOT/'runs/city_uptake_v3'/city/'fixture.json').read_text());vs=E.parse(ROOT/'runs/city_preflight_v1'/city/'accepted.xml').getroot().findall('vehicle');expected=[]
 for v in vs:
  if 310<=float(v.get('depart'))<370 and v.get('id') in fx['eligible_alternatives']:
   ident=v.get('id');u=int.from_bytes(hashlib.sha256(f'4101:{city}:{ident}'.encode()).digest()[:8],'big')/2**64
   expected.append(dict(id=ident,scheduled_departure_s=float(v.get('depart')),compliance_draw=u))
 assert expected==r['cohort']
 for q in [.25,.5,1]:assert sum(x['compliance_draw']<q for x in expected)==r['assigned'][str(q)]
 assert r['accepted']+r['excluded']==600
v=dict(passed=True,eligible_total=sum(r['eligible'] for r in out['cities']),inferential_readiness=False,reason='One eligible LA request, zero LA assigned at25/50%; one development seed; cannot support policy-effect or power claims.',recommendation='Keep window and scarcity finding. Increase independently predeclared episode blocks or acquire longer suitable traces before choosing confirmatory sample size. No outcome-based alignment search.')
(p/'verification.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
