"""Predeclared new-seed construction; no policy/traffic outcomes read."""
import fcntl,hashlib,json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
import sumo,sumolib
from v2x.credentials import ROOT
from audit_route_lanes import audit
from validate_city_uptake import alternate
O=ROOT/'runs/replication_cohorts_v1';B=ROOT/'.venv/bin'
PLAN=dict(stage='development_feasibility_not_confirmatory',cities=['los_angeles','luxembourg','pedralbes'],seeds=list(range(4201,4221)),requests=600,departure_window=[310,370],trace_epoch=300,trace_offsets=[0,90],fixed_incident='Retain v19 edge selected on development seed4101; do not reselect on new cohorts',demand='randomTrips,common preflight network,0..900s,period1.5,min600m,max2500m,fringe5',retention='No replacement of unroutable/lane-infeasible requests or empty cohorts. Record closed-endpoint incompatibility; do not execute such a block without a separate prospective incident protocol.',scope='60 independently initialized demand constructions, not60 independent radio recordings or completed traffic experiments',stop_rule='Exactly20 seeds per city; no stopping or seed selection by eligible count')
def save(p,x):p.write_text(json.dumps(x,indent=2))
def run(args,log):
 with log.open('w') as f:subprocess.run(list(map(str,args)),stdout=f,stderr=f,check=True)
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Complete')
  if (O/'plan.json').exists():assert json.loads((O/'plan.json').read_text())==PLAN
  else:save(O/'plan.json',PLAN)
  rows=[]
  for city in PLAN['cities']:
   n=ROOT/'runs/city_preflight_v1'/city/'city.net.xml';net=sumolib.net.readNet(str(n),withInternal=True);fx=json.loads((ROOT/'runs/city_uptake_v3'/city/'fixture.json').read_text());edge=fx['edge']
   for seed in PLAN['seeds']:
    p=O/city/str(seed);p.mkdir(parents=True,exist_ok=True)
    if (p/'result.json').exists():rows.append(json.loads((p/'result.json').read_text()));continue
    if not (p/'trips.xml').exists():run([B/'python',Path(sumo.__file__).parent/'tools/randomTrips.py','-n',n,'-o',p/'trips.xml','--seed',seed,'--begin',0,'--end',900,'--period',1.5,'--min-distance',600,'--max-distance',2500,'--fringe-factor',5,'--vehicle-class','passenger','--trip-attributes','departLane="best" departSpeed="max"'],p/'demand.log')
    if not (p/'routed.xml').exists():run([B/'duarouter','-n',n,'-r',p/'trips.xml','-o',p/'routed.xml','--seed',seed,'--ignore-errors','true','--no-step-log'],p/'routing.log')
    requested={v.get('id') for v in E.parse(p/'trips.xml').getroot().findall('trip')};tree=E.parse(p/'routed.xml');vs=tree.getroot().findall('vehicle');routed={v.get('id') for v in vs};check=audit(n,p/'routed.xml');bad={r['vehicle'] for r in check['failures']}
    for v in vs:
     if v.get('id') in bad:tree.getroot().remove(v)
    tree.write(p/'accepted.xml');vs=tree.getroot().findall('vehicle');candidates=[];no_alt=[];endpoints=[];altxml=E.Element('routes')
    for v in vs:
     ident=v.get('id');route=v.find('route').get('edges').split();dep=float(v.get('depart'))
     if edge in (route[0],route[-1]):endpoints.append(ident)
     if not (310<=dep<370 and edge in route):continue
     a=None if edge in (route[0],route[-1]) else alternate(net,route[0],route[-1],edge)
     if not a:no_alt.append(ident);continue
     E.SubElement(E.SubElement(altxml,'vehicle',id=ident),'route',edges=' '.join(a));candidates.append(dict(id=ident,depart=dep,route=a,draw=int.from_bytes(hashlib.sha256(f'{seed}:{city}:{ident}'.encode()).digest()[:8],'big')/2**64))
    E.ElementTree(altxml).write(p/'alternatives.xml');altcheck=audit(n,p/'alternatives.xml');altbad={r['vehicle'] for r in altcheck['failures']};cohort=[r for r in candidates if r['id'] not in altbad]
    row=dict(city=city,seed=seed,requested=len(requested),unroutable=len(requested-routed),lane_excluded=len(bad),accepted=len(vs),eligible=len(cohort),no_alternative=no_alt,alternative_lane_failures=altcheck['failures'],incident_endpoint_ids=endpoints,assigned={str(q):sum(r['draw']<q for r in cohort) for q in [.25,.5,1]},cohort=cohort)
    assert row['requested']==600==row['accepted']+row['unroutable']+row['lane_excluded'];save(p/'result.json',row);rows.append(row);print(city,seed,'eligible',len(cohort),'endpoints',len(endpoints),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
