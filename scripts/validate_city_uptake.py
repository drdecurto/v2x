"""Development pre-trip detour uptake; ideal information, no auditor/trace claim."""
import fcntl,hashlib,heapq,json,xml.etree.ElementTree as E
from collections import Counter
import sumolib,traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure
from audit_route_lanes import audit
O=ROOT/'runs/city_uptake_v3';S=ROOT/'runs/city_preflight_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def draw(city,ident):return int.from_bytes(hashlib.sha256(f'4101:{city}:{ident}'.encode()).digest()[:8],'big')/2**64
def alternate(net,start,end,blocked):
 queue=[(0.,start,(start,))];seen=set()
 while queue:
  cost,edge,path=heapq.heappop(queue)
  if edge in seen:continue
  seen.add(edge)
  if edge==end:return list(path)
  for nxt,conns in net.getEdge(edge).getOutgoing().items():
   nid=nxt.getID()
   if nid==blocked or nid in seen:continue
   if any(c.getFromLane().allows('passenger') and c.getToLane().allows('passenger') and (not c.getViaLaneID() or net.getLane(c.getViaLaneID()).allows('passenger')) for c in conns):
    heapq.heappush(queue,(cost+nxt.getLength()/nxt.getSpeed(),nid,path+(nid,)))
 return None

def fixture(city,p):
 if (p/'fixture.json').exists():return json.loads((p/'fixture.json').read_text())
 net=sumolib.net.readNet(str(S/city/'city.net.xml'),withInternal=True);tree=E.parse(S/city/'accepted.xml');routes={v.get('id'):v.find('route').get('edges').split() for v in tree.getroot().findall('vehicle')};endpoints={r[0] for r in routes.values()}|{r[-1] for r in routes.values()};counts=Counter(e for r in routes.values() for e in set(r[1:-1]));candidates=[e for e in counts if e not in endpoints and net.getEdge(e).getLength()>=60]
 blocked=min(candidates,key=lambda e:(-counts[e],e));alts={};no_path=[]
 for ident,r in routes.items():
  if blocked in r:
   alt=alternate(net,r[0],r[-1],blocked)
   if alt:alts[ident]=alt
   else:no_path.append(ident)
 test=E.Element('routes')
 for ident,r in alts.items():E.SubElement(E.SubElement(test,'vehicle',id=ident),'route',edges=' '.join(r))
 E.ElementTree(test).write(p/'candidate_routes.xml');check=audit(S/city/'city.net.xml',p/'candidate_routes.xml');bad={x['vehicle'] for x in check['failures']}
 fixture=dict(city=city,edge=blocked,street=net.getEdge(blocked).getName(),exposed=counts[blocked],eligible_alternatives={k:v for k,v in alts.items() if k not in bad},no_path=no_path,lane_rejected=check['failures'],draws={i:draw(city,i) for i in routes},selection='Highest route exposure among >=60m non-endpoint edges; lexical tie-break; no traffic outcomes used',source_hash=hashlib.sha256((S/city/'accepted.xml').read_bytes()).hexdigest())
 save(p/'fixture.json',fixture);return fixture

def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Completed')
  plan=dict(stage='development_mechanism_not_policy_effectiveness',cities=['los_angeles','luxembourg','pedralbes'],uptake=[0,.25,.5,1],seed=4101,closure_s=[0,900],end_s=2400,step_s=.5,emission_class='HBEFA3/PC_G_EU6',information='Perfect pre-trip closure notice; no transport or model latency, no semantic auditor. Only exposed trips with lane-feasible alternatives can divert.',compliance='Stable SHA256 city/seed/vehicle uniform draw; nested threshold, shared across arms.',route_rule='Deterministic free-flow shortest path avoiding closure, same candidate per vehicle in every arm; no online CO2 oracle',retention='Retain all preflight exclusions and unavailable alternative routes; do not replace demand')
  save(O/'plan.json',plan);rows=[]
  for city in plan['cities']:
   p=O/city;p.mkdir(exist_ok=True);fx=fixture(city,p)
   for fraction in plan['uptake']:
    out=p/str(fraction);out.mkdir(exist_ok=True)
    if (out/'result.json').exists():rows.append(json.loads((out/'result.json').read_text()));continue
    tree=E.parse(S/city/'accepted.xml');assigned=[];diverted=[]
    for typ in tree.getroot().findall('vType'):typ.set('emissionClass',plan['emission_class'])
    for v in tree.getroot().findall('vehicle'):
     ident=v.get('id')
     if fx['draws'][ident]<fraction:
      assigned.append(ident)
      if ident in fx['eligible_alternatives']:v.find('route').set('edges',' '.join(fx['eligible_alternatives'][ident]));diverted.append(ident)
    tree.write(out/'routes.xml',encoding='utf-8',xml_declaration=True);save(out/'assignment.json',dict(assigned=assigned,diverted=diverted))
    traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(S/city/'city.net.xml'),'-r',str(out/'routes.xml'),'--ignore-route-errors','true','--seed','4101','--step-length','.5','--time-to-teleport','-1','--device.emissions.probability','1','--tripinfo-output',str(out/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--statistic-output',str(out/'statistics.xml'),'--error-log',str(out/'errors.log'),'--no-step-log'],label='uptake',stdout=(out/'run.log').open('w'))
    c=traci.getConnection('uptake');closures=[LaneClosure(fx['edge']+'_'+str(i)) for i in range(c.edge.getLaneNumber(fx['edge']))];closed_entries=0
    try:
     for cl in closures:cl.close(c)
     for step in range(4800):
      if step==1800:
       for cl in closures:cl.reopen(c)
      c.simulationStep()
      if step<1800:closed_entries+=c.edge.getLastStepVehicleNumber(fx['edge'])
    finally:c.close()
    trips=list(E.parse(out/'tripinfo.xml').getroot());st=E.parse(out/'statistics.xml').getroot();co2=sum(float(t.find('emissions').get('CO2_abs')) for t in trips)/1e6;arrived=sum(float(t.get('arrival'))>=0 for t in trips);running=int(st.find('vehicles').get('running'));pending=int(st.find('vehicles').get('waiting'));accepted=len(tree.getroot().findall('vehicle'))
    row=dict(city=city,uptake=fraction,requested=600,accepted=accepted,excluded=600-accepted,arrived=arrived,running=running,pending=pending,assigned=len(assigned),diverted=len(diverted),exposed=fx['exposed'],co2_kg=co2,closed_edge_occupancy_samples=closed_entries,safety=st.find('safety').attrib,teleports=st.find('teleports').attrib)
    assert arrived+running+pending==accepted;save(out/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
