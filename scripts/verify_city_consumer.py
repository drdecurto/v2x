"""Reconcile saved decisions without importing consumer logic."""
import hashlib,json,xml.etree.ElementTree as E
from v2x.credentials import ROOT
p=ROOT/'runs/city_consumer_v1';rows=json.loads((p/'decisions.json').read_text())
assert len(rows)==84 and len({(r['city'],r['case'],r['policy']) for r in rows})==84
for name,digest in json.loads((p/'source_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
for row in rows:
 case,policy,r=row['case'],row['policy'],row['result']
 expected=case in ('supported','qualified') or (case=='unsupported_green' and policy!='content') or (case=='changed_version' and policy!='content')
 assert r['admit']==expected and r['route_selected']==expected
 if expected:
  fx=json.loads((ROOT/'runs/city_uptake_v3'/row['city']/'fixture.json').read_text())
  assert r['route']==fx['eligible_alternatives'][r['vehicle_id']] and fx['edge'] not in r['route']
  if policy in ('rules','deadline'):assert not r['text'] and '40%' not in r['delivered_text']
 else:assert r['route'] is None and r['delivered_text'] is None
summary=json.loads((p/'summary.json').read_text());assert summary['selected']==42 and summary['unsupported_free_text_admitted']==3
(p/'verification.json').write_text(json.dumps(dict(passed=True,decisions_checked=84,source_hashes_checked=6,selected_routes_checked=42,actual_traffic_runs=0),indent=2))
print('84 decision contracts; 42 selected routes; six source hashes verified. No traffic or model observations.')
