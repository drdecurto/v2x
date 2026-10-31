"""Independent saved-record checks; no inference or simulator reruns."""
import json, math
import pandas as pd
from v2x.credentials import ROOT
from v2x.evidence import EvidenceReceiver
from v2x.consumer import consume
O=ROOT/'runs/live_stream_v1'
read=lambda p:json.loads(p.read_text())
summary=read(O/'summary.json'); checks=[]
packets=pd.read_csv(ROOT/'data/derived/see_parkinglot_6.csv'); packets=packets[packets.tx_offset_s<=35].to_dict('records')
for mode in summary['plan']['modes']:
 d=O/mode; result=read(d/'result.json'); obs=read(d/'observations.json'); emissions=read(d/'emissions.json'); deliveries=read(d/'deliveries.json'); samples=read(d/'samples.json')
 assert len(samples)==400 and all(abs(s['sim_s']-(i+1)/10)<1e-8 for i,s in enumerate(samples))
 assert len(obs)==8 and all(o['road_A_closed']==(5<=o['observed_at_s']<18) for o in obs)
 assert all(s['true_closed']==(5<=s['sim_s']<18) for s in samples)
 assert result['closed_lane_entries']==0 and result['arrived'] and result['pending_steps']>0
 expected=[]
 for i,p in enumerate(packets):
  tx=5+p['tx_offset_s']; ob=max((o for o in obs if o['observed_at_s']<=tx),key=lambda o:o['observed_at_s'])
  e=emissions[i]; assert e['packet_index']==i and e['tx_s']==tx and e['sequence']==ob['sequence'] and e['received']==bool(p['received'])
  if p['received'] and tx+p['delay_s']<=40: expected.append((tx+p['delay_s'],i,ob))
 expected.sort(key=lambda x:(x[0],x[1])); assert len(expected)==len(deliveries)
 rx=EvidenceReceiver(5); statuses=[]; consumed=False
 for (native,idx,ob),delivery in zip(expected,deliveries):
  processed=math.ceil(native*10-1e-10)/10
  assert delivery['packet_index']==idx and abs(delivery['processed_s']-processed)<1e-8
  assert 0<=processed-native<=.1+1e-8
  # Insert consumer call after all receipts at its simulation step.
  if not consumed and processed>result['consume_sim_s']:
   assert rx.available(result['consume_sim_s'])==result['current_evidence']; consumed=True
  assert rx.receive(ob,processed)==delivery['status']
 rec=read(d/'audit.json'); assert math.isclose(result['service_s'],rec['finished_wall']-rec['started_wall'])
 assert result['consume_wall_s']+1e-8>=result['submit_wall_s']+result['queue_wait_s']+result['service_s']
 request=read(d/'request.json'); checkrx=EvidenceReceiver(5)
 checkrx.receive(result['current_evidence'],result['consume_sim_s'])
 road=next(s['road'] for s in samples if s['sim_s']==result['consume_sim_s'])
 decision=consume('content',request['advisory'],checkrx,result['consume_sim_s'],before_junction=road=='approach',audited=request['evidence'],verdict=rec.get('decision'))
 assert decision==result['decision'] and decision['admit']==result['acted']
 if mode=='fixed_2s': assert result['acted'] and decision['mode']=='content_accept'
 checks.append(dict(mode=mode,packet_records_checked=len(expected),decision=decision['mode'],pending_steps=result['pending_steps'],passed=True))
(O/'verification.json').write_text(json.dumps(checks,indent=2)); print(json.dumps(checks,indent=2))
