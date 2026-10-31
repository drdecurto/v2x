import json,fcntl,math
from pathlib import Path
import pandas as pd,traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure,passenger_allowed
from v2x.replay import replay_observations
from v2x.evidence import EvidenceReceiver
from v2x.consumer import consume
O=ROOT/'runs/consumer_stream_v1';O.mkdir(exist_ok=True)
plan={'profiles':[1,6],'close_s':22,'reopen_s':38,'observation_period_s':5,'age_limit_s':5,'audit_snapshot_s':21,'consume_times_s':[21.5,22.2,25.0001,25.6,27,50],'policies':['none','rules','content','deadline'],'verdict':'fixed accept; not a model measurement','scope':'shadow advisory decisions over SUMO permission truth with recorded LTE packet transport; no applied route changes or policy performance comparison'}
with (O/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (O/'summary.json').exists():raise SystemExit('Completed')
 (O/'plan.json').write_text(json.dumps(plan,indent=2));(O/'routes.xml').write_text('<routes><vehicle id="focal" depart="20"><route edges="approach main exit"/></vehicle></routes>')
 traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(O/'routes.xml'),'--step-length','.1','--seed','5101','--time-to-teleport','-1','--no-step-log','--error-log',str(O/'errors.log')],label='consumer',stdout=(O/'sumo.log').open('w'))
 c=traci.getConnection('consumer');closure=LaneClosure('main_0');observations=[];truth=[]
 try:
  for step in range(1,601):
   c.simulationStep();t=c.simulation.getTime()
   if step==220:closure.close(c)
   if step==380:closure.reopen(c)
   state={'t':t,'closed':not passenger_allowed(c,'main_0'),'road':c.vehicle.getRoadID('focal') if 'focal' in c.vehicle.getIDList() else None}
   truth.append(state)
   if step%50==0:observations.append(dict(source_id='rsu',sequence=step//50,observed_at_s=t,road_A_closed=state['closed'],road_B_available=passenger_allowed(c,'detour1_0') and passenger_allowed(c,'detour2_0')))
 finally:c.close()
 (O/'truth.json').write_text(json.dumps(truth));(O/'observations.json').write_text(json.dumps(observations,indent=2));rows=[]
 for profile in plan['profiles']:
  packets=pd.read_csv(ROOT/f'data/derived/see_parkinglot_{profile}.csv');packets=packets[packets.tx_offset_s<=55].to_dict('records');_,arrivals=replay_observations(packets,observations,epoch_s=5,max_age_s=5)
  rx=EvidenceReceiver(5);j=0;byseq={x['sequence']:x for x in observations}
  def advance(t):
   global j
   while j<len(arrivals) and arrivals[j]['rx_s']<=t:
    d=arrivals[j];rx.receive(byseq[d['observation_sequence']],d['rx_s']);j+=1
  advance(21);audited=rx.available(21);assert audited is not None
  advisory={'issued_s':21,'expires_s':45,'road':'A','action':'main','claimed_closed':False}
  for now in plan['consume_times_s']:
   advance(now);world=truth[min(int(math.floor(now*10+1e-7))-1,len(truth)-1)]
   for policy in plan['policies']:
    result=consume(policy,advisory,rx,now,before_junction=world['road']=='approach',audited=audited,verdict='accept',deadline_fallback=policy=='deadline')
    rows.append(dict(profile=profile,policy=policy,time_s=now,decision=result,received_sequence=rx.current['sequence'] if rx.current else None,true_closed=world['closed'],focal_road=world['road'],admitted_closed_road_advisory=result['admit'] and world['closed']))
 (O/'decisions.json').write_text(json.dumps(rows,indent=2))
 summary={'decisions':len(rows),'hidden_change_admissions':sum(x['admitted_closed_road_advisory'] for x in rows),'scope':plan['scope'],'checks':[{'time':t,'results':[(x['profile'],x['policy'],x['decision']['mode']) for x in rows if x['time_s']==t]} for t in plan['consume_times_s']]}
 (O/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
