"""Development stress validation, perfect information and full cohort uptake.
No communication or policy-effect claims. All predeclared blocks retained.
"""
import fcntl, hashlib, json, xml.etree.ElementTree as E
from decimal import Decimal
import traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure
O=ROOT/'runs/paired_city_stress_v1/no_diversion'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  source=json.loads((ROOT/'runs/replication_incidents_v1/plan.json').read_text())
  plan=dict(stage='prospectively_narrowed_development_scenario',cities=source['cities'],seeds=list(range(4201,4221)),closure_s=[0,900],end_s=2400,step_s=.5,information='Perfect incident information; no communication or inference',uptake=0,decision='Once at actual departure for scheduled cohort, if still on first edge',all_blocks_retained=True,selection='All twenty existing development seeds; frozen paired sensitivity, not a simulator repair',inference_calls=0)
  if (O/'plan.json').exists():assert json.loads((O/'plan.json').read_text())==plan
  else:save(O/'plan.json',plan)
  rows=[]
  for city in plan['cities']:
   for seed in plan['seeds']:
    p=O/city/str(seed);p.mkdir(parents=True,exist_ok=True)
    if (p/'result.json').exists():rows.append(json.loads((p/'result.json').read_text()));continue
    if (p/'started.json').exists():raise RuntimeError(f'Interrupted block needs review: {p}')
    fxpath=ROOT/'runs/replication_incidents_v1'/city/str(seed)/'result.json';fx=json.loads(fxpath.read_text());src=ROOT/'runs/replication_cohorts_v1'/city/str(seed)/'accepted.xml'
    assert hashlib.sha256(src.read_bytes()).hexdigest()==fx['input_sha256']
    save(p/'started.json',dict(city=city,seed=seed,fixture_sha256=hashlib.sha256(fxpath.read_bytes()).hexdigest()))
    tree=E.parse(src);original={v.get('id'):v.find('route').get('edges').split() for v in tree.getroot().findall('vehicle')};cohort={v['id']:v for v in fx['cohort']}
    for typ in tree.getroot().findall('vType'):typ.set('emissionClass','HBEFA3/PC_G_EU6')
    tree.write(p/'routes.xml');log=(p/'sumo.log').open('w')
    traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'runs/city_preflight_v1'/city/'city.net.xml'),'-r',str(p/'routes.xml'),'--ignore-route-errors','true','--seed',str(seed),'--step-length','.5','--time-to-teleport','-1','--device.emissions.probability','1','--tripinfo-output',str(p/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--statistic-output',str(p/'statistics.xml'),'--error-log',str(p/'errors.log'),'--no-step-log'],label='dynamic',stdout=log)
    c=traci.getConnection('dynamic');closures=[LaneClosure(fx['edge']+'_'+str(i)) for i in range(c.edge.getLaneNumber(fx['edge']))];decisions=[];entries=[];grandfather=[];previous=set();occupancy=0
    try:
     for step in range(4801):
      now=step*.5
      if step==0:
       grandfather=list(c.edge.getLastStepVehicleIDs(fx['edge']));previous=set(grandfather)
       for cl in closures:cl.close(c)
      if step==1800:
       for cl in closures:cl.reopen(c)
      if 0<step<1800:
       current=set(c.edge.getLastStepVehicleIDs(fx['edge']));occupancy+=len(current)
       entries.extend(dict(time_s=now,vehicle_id=v) for v in sorted(current-previous));previous=current
      if step:
       for ident in c.simulation.getDepartedIDList():
        if ident not in cohort:continue
        d=dict(vehicle_id=ident,time_s=now,applied=False,error=None)
        if not 0<=now<900:d['error']='outside_incident_window'
        elif c.vehicle.getRoadID(ident)!=original[ident][0]:d['error']='first_edge_passed'
        else:
         try:d['error']='assigned_no_diversion'
         except traci.TraCIException as exc:d['error']=str(exc)
        d['route_after']=list(c.vehicle.getRoute(ident));decisions.append(d)
      if step<4800:c.simulationStep()
    finally:c.close();log.close();save(p/'decisions.json',decisions);save(p/'closure_entries.json',entries)
    trips=E.parse(p/'tripinfo.xml').getroot().findall('tripinfo');st=E.parse(p/'statistics.xml').getroot()
    row=dict(city=city,seed=seed,accepted=len(original),excluded=600-len(original),eligible=len(cohort),decisions=len(decisions),applied=sum(d['applied'] for d in decisions),decision_failures=[d for d in decisions if not d['applied']],arrived=sum(float(t.get('arrival'))>=0 for t in trips),running=int(st.find('vehicles').get('running')),pending=int(st.find('vehicles').get('waiting')),co2_kg=str(sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/Decimal(1000000)),grandfathered=grandfather,new_closed_edge_entries=len(entries),closed_occupancy_samples=occupancy,safety=st.find('safety').attrib,teleports=st.find('teleports').attrib)
    row['accounting_valid']=row['arrived']+row['running']+row['pending']==len(original)
    save(p/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
