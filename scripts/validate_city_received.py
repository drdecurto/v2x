"""Three-city development integration; deterministic templates, finite LTE replay."""
import fcntl,hashlib,heapq,json,xml.etree.ElementTree as E
import pandas as pd,traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure,passenger_allowed
from v2x.evidence import EvidenceReceiver
from v2x.city_consumer import consume_city
O=ROOT/'runs/city_received_v1';S=ROOT/'runs/city_preflight_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Complete')
  plan=dict(stage='development_integration',cities=['los_angeles','luxembourg','pedralbes'],seed=4101,profile=6,epoch_s=0,observation_period_s=5,max_age_s=5,step_s=.5,end_s=2400,closure_s=[0,900],compliance=.5,policy='rules',decision='Once on departure, only if still on original first edge; no later retry',communication='One shared finite stationary LTE link per city; no looping/time scaling; all late departures retain unavailable evidence',inference_calls=0)
  save(O/'plan.json',plan);path=ROOT/'data/derived/see_parkinglot_6.csv';packets=pd.read_csv(path).to_dict('records');save(O/'trace_hash.json',{'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});rows=[]
  for city in plan['cities']:
   p=O/city;p.mkdir(exist_ok=True)
   if (p/'result.json').exists():rows.append(json.loads((p/'result.json').read_text()));continue
   if (p/'started.json').exists():raise RuntimeError('Interrupted city requires review')
   save(p/'started.json',{'city':city});fx=json.loads((ROOT/'runs/city_uptake_v3'/city/'fixture.json').read_text());tree=E.parse(S/city/'accepted.xml');original={v.get('id'):v.find('route').get('edges').split() for v in tree.getroot().findall('vehicle')}
   for typ in tree.getroot().findall('vType'):typ.set('emissionClass','HBEFA3/PC_G_EU6')
   tree.write(p/'routes.xml');traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(S/city/'city.net.xml'),'-r',str(p/'routes.xml'),'--ignore-route-errors','true','--seed','4101','--step-length','.5','--time-to-teleport','-1','--device.emissions.probability','1','--tripinfo-output',str(p/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--statistic-output',str(p/'statistics.xml'),'--error-log',str(p/'errors.log'),'--no-step-log'],label='received',stdout=(p/'sumo.log').open('w'))
   c=traci.getConnection('received');closures=[LaneClosure(fx['edge']+'_'+str(i)) for i in range(c.edge.getLaneNumber(fx['edge']))];receiver=EvidenceReceiver(5);queue=[];i=0;obs=[];decisions=[];deliveries=[];sent=[];occupancy=0
   try:
    for cl in closures:cl.close(c)
    for step in range(4801):
     now=step*.5
     if step==1800:
      for cl in closures:cl.reopen(c)
     if step%10==0:
      obs.append(dict(source_id=city,sequence=step//10,observed_at_s=now,road_A_closed=not passenger_allowed(c,fx['edge']+'_0'),road_B_available=True))
     while i<len(packets) and packets[i]['tx_offset_s']<=now:
      packet=packets[i];tx=float(packet['tx_offset_s']);ob=obs[int(tx//5)];rec=dict(index=i,tx_s=tx,received=bool(packet['received']),sequence=ob['sequence'])
      if rec['received']:heapq.heappush(queue,(tx+float(packet['delay_s']),i,dict(ob)))
      sent.append(rec);i+=1
     while queue and queue[0][0]<=now:
      arrival,index,ob=heapq.heappop(queue);status=receiver.receive(ob,now);deliveries.append(dict(index=index,rx_s=arrival,processed_s=now,status=status,sequence=ob['sequence']))
     if step:
      for ident in c.simulation.getDepartedIDList():
       if ident not in fx['eligible_alternatives']:continue
       evidence=receiver.available(now);road=c.vehicle.getRoadID(ident);a=dict(issued_s=now,expires_s=now+5,road='A',action='detour',claimed_closed=True,text='A closure is reported. Consider the alternative; no emissions saving is guaranteed.')
       d=consume_city('rules',a,receiver,now,vehicle_id=ident,original_route=original[ident],alternative_route=fx['eligible_alternatives'][ident],before_decision=road==original[ident][0],compliant=fx['draws'][ident]<.5)
       applied=False
       if d['route_selected']:c.vehicle.setRoute(ident,d['route']);applied=True
       decisions.append(dict(time_s=now,evidence=evidence,result=d,route_applied=applied,route_after=list(c.vehicle.getRoute(ident))))
     if step<1800:occupancy+=c.edge.getLastStepVehicleNumber(fx['edge'])
     if step<4800:c.simulationStep()
   finally:
    c.close()
    for name,x in [('observations',obs),('decisions',decisions),('deliveries',deliveries),('sent',sent)]:save(p/(name+'.json'),x)
   trips=list(E.parse(p/'tripinfo.xml').getroot());st=E.parse(p/'statistics.xml').getroot();row=dict(city=city,requested=600,accepted=len(original),excluded=600-len(original),arrived=sum(float(t.get('arrival'))>=0 for t in trips),running=int(st.find('vehicles').get('running')),pending=int(st.find('vehicles').get('waiting')),co2_kg=sum(float(t.find('emissions').get('CO2_abs')) for t in trips)/1e6,decisions=len(decisions),applied=sum(d['route_applied'] for d in decisions),unavailable=sum(d['result']['mode']=='evidence_unavailable' for d in decisions),closed_edge_occupancy_samples=occupancy,safety=st.find('safety').attrib,teleports=st.find('teleports').attrib)
   assert row['arrived']+row['running']+row['pending']==len(original);save(p/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
