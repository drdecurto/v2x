"""Prospective endpoint-safe construction on all predeclared development blocks."""
import fcntl,hashlib,json,xml.etree.ElementTree as E
from collections import Counter
import sumolib
from v2x.credentials import ROOT
from validate_city_uptake import alternate
from audit_route_lanes import audit
O=ROOT/'runs/replication_incidents_v1';S=ROOT/'runs/replication_cohorts_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Complete')
  plan=dict(stage='development_after_fixed_edge_feasibility_failure',seeds=list(range(4201,4221)),cities=['los_angeles','luxembourg','pedralbes'],edge_rule='>=60m passenger edge, no original trip endpoint, maximal exposure over all accepted routes, lexical tie-break; never optimize advisory-window count or outcomes',cohort='Scheduled departure [310,370), incident exposure, existing legal-lane alternative',no_replenishment=True,no_outcome_data=True,stop_rule='All60 blocks, including empty cohorts; same36,000 requested trips as construction audit')
  save(O/'plan.json',plan);rows=[]
  for city in plan['cities']:
   n=ROOT/'runs/city_preflight_v1'/city/'city.net.xml';net=sumolib.net.readNet(str(n),withInternal=True)
   for seed in plan['seeds']:
    p=O/city/str(seed);p.mkdir(parents=True,exist_ok=True);rp=S/city/str(seed)/'accepted.xml';vs=E.parse(rp).getroot().findall('vehicle');routes={v.get('id'):v.find('route').get('edges').split() for v in vs};endpoints={x for r in routes.values() for x in [r[0],r[-1]]};counts=Counter(e for r in routes.values() for e in set(r[1:-1]));c=[e for e in counts if e not in endpoints and net.getEdge(e).getLength()>=60];edge=min(c,key=lambda e:(-counts[e],e));alts=E.Element('routes');cohort=[];unavailable=[]
    for v in vs:
     ident=v.get('id');r=routes[ident];dep=float(v.get('depart'))
     if not(310<=dep<370 and edge in r):continue
     alt=alternate(net,r[0],r[-1],edge)
     if alt is None:unavailable.append(ident);continue
     E.SubElement(E.SubElement(alts,'vehicle',id=ident),'route',edges=' '.join(alt));cohort.append(dict(id=ident,depart=dep,route=alt,draw=int.from_bytes(hashlib.sha256(f'{seed}:{city}:{ident}'.encode()).digest()[:8],'big')/2**64))
    E.ElementTree(alts).write(p/'alternatives.xml');check=audit(n,p/'alternatives.xml');bad={r['vehicle'] for r in check['failures']};cohort=[r for r in cohort if r['id'] not in bad]
    prior=json.loads((S/city/str(seed)/'result.json').read_text());row={k:prior[k] for k in ['city','seed','requested','accepted','unroutable','lane_excluded']};row.update(edge=edge,exposure_all_routes=counts[edge],eligible=len(cohort),cohort=cohort,no_alternative=unavailable,alternative_lane_failures=check['failures'],assigned={str(q):sum(r['draw']<q for r in cohort) for q in [.25,.5,1]},input_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());save(p/'result.json',row);rows.append(row)
  save(O/'summary.json',rows)
  aggregate=[]
  for city in plan['cities']:
   rs=[r for r in rows if r['city']==city];aggregate.append(dict(city=city,blocks=len(rs),requested=sum(r['requested'] for r in rs),accepted=sum(r['accepted'] for r in rs),eligible=sum(r['eligible'] for r in rs),eligible_min=min(r['eligible'] for r in rs),eligible_max=max(r['eligible'] for r in rs),empty_blocks=sum(r['eligible']==0 for r in rs),assigned={str(q):sum(r['assigned'][str(q)] for r in rs) for q in [.25,.5,1]},distinct_incident_edges=len(set(r['edge'] for r in rs))))
  save(O/'aggregate.json',aggregate);print(json.dumps(aggregate,indent=2))
if __name__=='__main__':main()
