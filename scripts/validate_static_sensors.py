"""Fixed-signal development baseline with regenerated advisory sensors."""
import fcntl,json,hashlib,xml.etree.ElementTree as E
import sumolib,traci
from v2x.credentials import ROOT
O=ROOT/'runs/static_sensors_v1';SOURCE=ROOT/'runs/city_preflight_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Completed')
  plan=dict(cities=['los_angeles','luxembourg','pedralbes'],seed=4101,horizon_s=2400,step_s=.5,period_s=5,signal_rule='Change type to static only; preserve phase states, duration, offset and next attributes.',sensor_rule='12 highest accepted-demand weighted signal controllers, deterministic ID tie break; E2 on passenger approaches longer than10m, at most80m; sensors observe only.',scope='Development baseline, no policy comparison or field calibration')
  save(O/'plan.json',plan);rows=[]
  for city in plan['cities']:
   p=O/city;p.mkdir(exist_ok=True)
   if (p/'result.json').exists():rows.append(json.loads((p/'result.json').read_text()));continue
   tree=E.parse(SOURCE/city/'city.net.xml')
   for tls in tree.getroot().findall('tlLogic'):tls.set('type','static')
   net=p/'city.net.xml';tree.write(net,encoding='utf-8',xml_declaration=True)
   routes=SOURCE/city/'accepted.xml';n=sumolib.net.readNet(str(net));counts={}
   for r in E.parse(routes).getroot().iter('route'):
    for edge in r.get('edges','').split():counts[edge]=counts.get(edge,0)+1
   ranked=sorted(n.getTrafficLights(),key=lambda t:(-sum(counts.get(c[0].getEdge().getID(),0) for c in t.getConnections()),t.getID()))[:12]
   add=E.Element('additional');rsus=[];sensors=[]
   for k,t in enumerate(ranked):
    lanes={c[0].getID():c[0] for c in t.getConnections() if c[0].allows('passenger') and c[0].getLength()>10}
    rsus.append(dict(id=f'RSU_{k}',tls=t.getID()))
    for j,(lid,lane) in enumerate(sorted(lanes.items())):
     length=min(80,lane.getLength()-2);ident=f'E2_{k}_{j}'
     E.SubElement(add,'laneAreaDetector',id=ident,lane=lid,pos=str(lane.getLength()-length-1),length=str(length),period='10',file=str(p/'detector_intervals.xml'),friendlyPos='true')
     sensors.append(dict(id=ident,lane=lid,tls=t.getID()))
   E.ElementTree(add).write(p/'sensors.add.xml',encoding='utf-8',xml_declaration=True);save(p/'infrastructure.json',dict(rsus=rsus,sensors=sensors))
   save(p/'inputs.json',{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [net,routes,p/'sensors.add.xml']})
   traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(net),'-r',str(routes),'-a',str(p/'sensors.add.xml'),'--seed','4101','--end','2400','--step-length','.5','--time-to-teleport','-1','--tripinfo-output',str(p/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--statistic-output',str(p/'statistics.xml'),'--error-log',str(p/'errors.log'),'--no-step-log'],label=city,stdout=(p/'run.log').open('w'))
   c=traci.getConnection(city);records=0;positive=0
   try:
    with (p/'observations.jsonl').open('w') as f:
     for step in range(1,4801):
      c.simulationStep();now=c.simulation.getTime()
      if step%10:continue
      for r in rsus:
       det=[dict(id=s['id'],vehicles=c.lanearea.getLastStepVehicleNumber(s['id']),halting=c.lanearea.getLastStepHaltingNumber(s['id']),occupancy_pct=c.lanearea.getLastStepOccupancy(s['id'])) for s in sensors if s['tls']==r['tls']]
       record=dict(source_id=r['id'],sequence=step//10,observed_at_s=now,tls=r['tls'],signal_state=c.trafficlight.getRedYellowGreenState(r['tls']),next_switch_s=c.trafficlight.getNextSwitch(r['tls']),controller='static',detectors=det)
       f.write(json.dumps(record)+'\n');records+=1;positive+=any(d['vehicles']>0 for d in det)
   finally:c.close()
   st=E.parse(p/'statistics.xml').getroot();tr=list(E.parse(p/'tripinfo.xml').getroot());v=st.find('vehicles')
   row=dict(city=city,accepted=len(E.parse(routes).getroot().findall('vehicle')),arrived=sum(float(t.get('arrival'))>=0 for t in tr),running=int(v.get('running')),pending=int(v.get('waiting')),rsus=len(rsus),detectors=len(sensors),records=records,positive_records=positive,safety=st.find('safety').attrib,teleports=st.find('teleports').attrib)
   assert row['accepted']==row['arrived']+row['running']+row['pending']
   save(p/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
