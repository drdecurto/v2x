"""Reconcile dynamic evidence independently of the simulation runner."""
import json,hashlib,xml.etree.ElementTree as E
from decimal import Decimal
from v2x.credentials import ROOT
p=ROOT/'runs/replication_dynamics_v1';plan=json.loads((p/'plan.json').read_text());rows=[]
for city in plan['cities']:
 for seed in plan['seeds']:
  d=p/city/str(seed);r=json.loads((d/'result.json').read_text());fxp=ROOT/'runs/replication_incidents_v1'/city/str(seed)/'result.json';fx=json.loads(fxp.read_text());cohort={x['id']:x for x in fx['cohort']};dec=json.loads((d/'decisions.json').read_text());trips=E.parse(d/'tripinfo.xml').getroot().findall('tripinfo');st=E.parse(d/'statistics.xml').getroot()
  assert json.loads((d/'started.json').read_text())['fixture_sha256']==hashlib.sha256(fxp.read_bytes()).hexdigest()
  assert r['accepted']==fx['accepted'] and r['excluded']+r['accepted']==600
  assert r['arrived']==sum(float(t.get('arrival'))>=0 for t in trips)
  assert r['running']==int(st.find('vehicles').get('running')) and r['pending']==int(st.find('vehicles').get('waiting'))
  assert r['arrived']+r['running']+r['pending']==r['accepted']
  assert Decimal(r['co2_kg'])==sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/1000000
  assert len({x['vehicle_id'] for x in dec})==len(dec)
  assert r['eligible']==len(cohort) and r['decisions']==len(dec)
  original={v.get('id') for v in E.parse(d/'routes.xml').getroot().findall('vehicle')}
  assert len({t.get('id') for t in trips})==len(trips) and all(t.get('id') in original for t in trips)
  for x in dec:
   assert x['vehicle_id'] in cohort
   if x['applied']:assert x['route_after']==cohort[x['vehicle_id']]['route'] and 300<=x['time_s']<900
  assert r['applied']==sum(x['applied'] for x in dec)
  assert r['new_closed_edge_entries']==len(json.loads((d/'closure_entries.json').read_text()))
  assert r['safety']==st.find('safety').attrib and r['teleports']==st.find('teleports').attrib
  rows.append(r)
summary={}
for city in plan['cities']:
 rr=[r for r in rows if r['city']==city]
 summary[city]={k:sum(r[k] for r in rr) for k in ['accepted','excluded','eligible','decisions','applied','arrived','running','pending','new_closed_edge_entries']}
 summary[city]['blocks']=len(rr);summary[city]['grandfathered']=sum(len(r['grandfathered']) for r in rr)
 for field in ['safety','teleports']:
  summary[city][field]={k:sum(int(r[field][k]) for r in rr) for k in rr[0][field]}
result=dict(accounting_and_record_checks='passed',blocks=len(rows),summary=summary,note='Record consistency does not imply safety validation passed; retain emergency stops and other failures.')
(p/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
