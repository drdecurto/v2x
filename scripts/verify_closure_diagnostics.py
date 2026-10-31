"""Independent record and topology checks for outcome-selected diagnostics."""
import json,hashlib,xml.etree.ElementTree as E
from decimal import Decimal
import sumolib
from v2x.credentials import ROOT
out=ROOT/'runs/closure_transition_v1';rows=json.loads((out/'summary.json').read_text());checked=[]
for r in rows:
 p=out/r['city']/str(r['seed']);source=ROOT/'runs/replication_dynamics_v1'/r['city']/str(r['seed'])
 prior=json.loads((source/'closure_entries.json').read_text());assert sorted(prior,key=str)==sorted(r['entries_reproduced'],key=str)
 fx=json.loads((ROOT/'runs/replication_incidents_v1'/r['city']/str(r['seed'])/'result.json').read_text());netpath=ROOT/'runs/city_preflight_v1'/r['city']/'city.net.xml';net=sumolib.net.readNet(str(netpath),withInternal=True)
 hashes=json.loads((p/'started.json').read_text());assert hashes['net_sha256']==hashlib.sha256(netpath.read_bytes()).hexdigest();assert hashes['routes_sha256']==hashlib.sha256((source/'routes.xml').read_bytes()).hexdigest()
 assert all('passenger' in x for x in json.loads((p/'permissions.json').read_text()).values())
 at300=next(x['vehicles'] for x in json.loads((p/'snapshots.json').read_text()) if x['time_s']==300)
 assert at300==r['at_closure'] and set(at300)=={x['vehicle_id'] for x in prior}
 for ident,s in at300.items():
  assert s['road'].startswith(':')
  todo=[net.getLane(s['lane'])];seen=set();reachable=False
  while todo:
   lane=todo.pop()
   if lane.getID() in seen:continue
   seen.add(lane.getID())
   for conn in lane.getOutgoing():
    target=conn.getToLane()
    if target.getEdge().getID()==fx['edge']:reachable=True
    elif target.getEdge().getID().startswith(':'):todo.append(target)
  assert reachable
  checked.append(dict(city=r['city'],seed=r['seed'],vehicle_id=ident,internal_lane=s['lane'],connects_to_incident=True))
base=ROOT/'runs/selected_no_closure_v1';controls=json.loads((base/'summary.json').read_text());comparisons=[]
priorall=json.loads((ROOT/'runs/replication_dynamics_v1/summary.json').read_text())
for row in controls:
 city=row['city'];seed=row['seed'];p=base/city/str(seed);prior=ROOT/'runs/replication_dynamics_v1'/city/str(seed)
 expected=max((r for r in priorall if r['city']==city),key=lambda r:(r['running'],-r['seed']));assert seed==expected['seed']
 assert (p/'routes.xml').read_bytes()==(prior/'routes.xml').read_bytes()
 trips=E.parse(p/'tripinfo.xml').getroot().findall('tripinfo');st=E.parse(p/'statistics.xml').getroot();assert row['arrived']==sum(float(t.get('arrival'))>=0 for t in trips)
 assert row['arrived']+row['running']+row['pending']==row['accepted']
 assert row['running']==int(st.find('vehicles').get('running')) and row['pending']==int(st.find('vehicles').get('waiting'))
 assert Decimal(row['co2_kg'])==sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/1000000
 decisions=json.loads((p/'decisions.json').read_text());before=json.loads((prior/'decisions.json').read_text())
 assert [(d['vehicle_id'],d['time_s'],d['applied'],d['route_after']) for d in decisions]==[(d['vehicle_id'],d['time_s'],d['applied'],d['route_after']) for d in before]
 assert row['safety']==st.find('safety').attrib and row['teleports']==st.find('teleports').attrib
 comparisons.append(dict(city=city,seed=seed,running_with_closure=expected['running'],running_without_closure=row['running'],same_departure_detours=True))
result=dict(passed=True,transition_blocks=len(rows),entries=len(checked),topology=checked,selected_controls=comparisons,scope='Outcome-selected development diagnostics; no population effect estimate')
(out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='topology'},indent=2))
