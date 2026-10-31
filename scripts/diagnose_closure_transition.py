"""Outcome-selected development diagnostic of every recorded post-closure entrant."""
import json,fcntl,hashlib
import traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure
O=ROOT/'runs/closure_transition_v1';S=ROOT/'runs/replication_dynamics_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  cases=[]
  for p in sorted(S.glob('*/*/closure_entries.json')):
   entries=json.loads(p.read_text())
   if entries:cases.append(dict(city=p.parent.parent.name,seed=int(p.parent.name),entries=entries))
  plan=dict(stage='outcome_selected_development_diagnostic',selection='All blocks with post-closure entries in replication_dynamics_v1; not representative effect estimation',end_s=305,step_s=.5,closure_s=300,record_s=[298,305],cases=cases,inference_calls=0)
  if (O/'plan.json').exists():assert json.loads((O/'plan.json').read_text())==plan
  else:save(O/'plan.json',plan)
  summary=[]
  for case in cases:
   city=case['city'];seed=case['seed'];p=O/city/str(seed);p.mkdir(parents=True,exist_ok=True)
   if (p/'result.json').exists():summary.append(json.loads((p/'result.json').read_text()));continue
   if (p/'started.json').exists():raise RuntimeError('Interrupted diagnostic needs review')
   fx=json.loads((ROOT/'runs/replication_incidents_v1'/city/str(seed)/'result.json').read_text());routes=S/city/str(seed)/'routes.xml';net=ROOT/'runs/city_preflight_v1'/city/'city.net.xml'
   save(p/'started.json',dict(routes_sha256=hashlib.sha256(routes.read_bytes()).hexdigest(),net_sha256=hashlib.sha256(net.read_bytes()).hexdigest()))
   log=(p/'sumo.log').open('w');traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(net),'-r',str(routes),'--ignore-route-errors','true','--seed',str(seed),'--step-length','.5','--time-to-teleport','-1','--device.emissions.probability','1','--error-log',str(p/'errors.log'),'--no-step-log'],label='transition',stdout=log)
   c=traci.getConnection('transition');cl=[LaneClosure(fx['edge']+'_'+str(i)) for i in range(c.edge.getLaneNumber(fx['edge']))];targets={r['vehicle_id'] for r in case['entries']};snap=[];entries=[];previous=set()
   try:
    for step in range(611):
     now=step*.5
     if step>=596:
      active=set(c.vehicle.getIDList())
      snap.append(dict(time_s=now,vehicles={v:dict(road=c.vehicle.getRoadID(v),lane=c.vehicle.getLaneID(v),position_m=c.vehicle.getLanePosition(v),speed_m_s=c.vehicle.getSpeed(v),route_index=c.vehicle.getRouteIndex(v)) for v in sorted(targets & active)}))
     if step==600:
      previous=set(c.edge.getLastStepVehicleIDs(fx['edge']))
      for x in cl:x.close(c)
      save(p/'permissions.json',{x.lane:list(c.lane.getDisallowed(x.lane)) for x in cl})
     if step>600:
      current=set(c.edge.getLastStepVehicleIDs(fx['edge']));entries.extend(dict(time_s=now,vehicle_id=v) for v in sorted(current-previous));previous=current
     if step<610:c.simulationStep()
   finally:c.close();log.close();save(p/'snapshots.json',snap)
   assert sorted(entries,key=lambda x:(x['time_s'],x['vehicle_id']))==sorted(case['entries'],key=lambda x:(x['time_s'],x['vehicle_id']))
   at300=next(s for s in snap if s['time_s']==300)['vehicles'];row=dict(city=city,seed=seed,entries_reproduced=entries,at_closure=at300,all_on_internal_lanes=all(x['road'].startswith(':') for x in at300.values()),target_count=len(targets));save(p/'result.json',row);summary.append(row)
  save(O/'summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
