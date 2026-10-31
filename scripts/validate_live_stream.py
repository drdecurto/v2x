"""Prospective development integration: online SUMO, native LTE and async audit.

No remote calls. Raw packet records remain local. Each episode has one audit;
40 seconds are paced, and trip completion is subsequently accelerated.
"""
import bisect, concurrent.futures, fcntl, hashlib, heapq, json, time
import xml.etree.ElementTree as ET
import httpx, pandas as pd, traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure, passenger_allowed
from v2x.evidence import EvidenceReceiver
from v2x.consumer import consume
from validate_async import audit, MODEL
from profile_nebius import SYSTEM

OUT = ROOT / 'runs/live_stream_v1'
PLAN = dict(stage='development_not_confirmatory', modes=['fixed_2s','ollama'],
            profile=6, epoch_s=5, step_s=.1, paced_s=40, seed=6101,
            close_s=5, reopen_s=18, observation_period_s=5, max_age_s=5,
            issue_s=11, expires_s=36, policy='content', remote_calls=0,
            receipt_rule='Native arrivals processed at next SUMO step; no future observation at transmission.',
            inference='One local call; no retry, no warm-up; failures retained.',
            scope='Component integration, not a policy-effectiveness or latency-distribution estimate.')

def save(path, data): path.write_text(json.dumps(data, indent=2))

def episode(mode, packets):
    out=OUT/mode; out.mkdir(exist_ok=True)
    if (out/'result.json').exists(): return json.loads((out/'result.json').read_text())
    # A started but unfinished episode requires review, not silent repeat inference.
    if (out/'started.json').exists(): raise RuntimeError('Interrupted episode requires review: '+mode)
    save(out/'started.json', {'at_unix_s':time.time()})
    (out/'routes.xml').write_text('<routes><vType id="car" vClass="passenger" accel="2.6" decel="4.5" sigma="0.5"/><route id="direct" edges="approach main exit"/><vehicle id="focal" type="car" route="direct" depart="0" departSpeed="max"/></routes>')
    traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(out/'routes.xml'),'--seed',str(PLAN['seed']),'--step-length','.1','--no-step-log','true','--time-to-teleport','-1','--tripinfo-output',str(out/'trips.xml'),'--tripinfo-output.write-unfinished','true','--error-log',str(out/'errors.log')],label=mode,stdout=(out/'sumo.log').open('w'))
    c=traci.getConnection(mode); closure=LaneClosure('main_0'); rx=EvidenceReceiver(5)
    observations=[]; stamps=[]; emissions=[]; deliveries=[]; queue=[]; samples=[]; i=0
    pool=concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future=None; handled=False; origin=time.monotonic(); result=dict(mode=mode, acted=False)
    try:
        for step in range(1,401):
            target=step/10; time.sleep(max(0,origin+target-time.monotonic()))
            c.simulationStep(); now=c.simulation.getTime()
            if step==50: closure.close(c)
            if step==180: closure.reopen(c)
            road=c.vehicle.getRoadID('focal') if 'focal' in c.vehicle.getIDList() else None
            closed=not passenger_allowed(c,'main_0')
            if step%50==0:
                observations.append(dict(source_id='rsu',sequence=step//50,observed_at_s=now,road_A_closed=closed,road_B_available=passenger_allowed(c,'detour1_0') and passenger_allowed(c,'detour2_0'))); stamps.append(now)
            while i<len(packets) and 5+packets[i]['tx_offset_s']<=now+1e-9:
                p=packets[i]; tx=5+p['tx_offset_s']; k=bisect.bisect_right(stamps,tx)-1
                assert k>=0
                ob=observations[k]; rec=dict(packet_index=i,tx_s=tx,sequence=ob['sequence'],received=bool(p['received']))
                if rec['received']:
                    rec['native_rx_s']=tx+p['delay_s']; heapq.heappush(queue,(rec['native_rx_s'],i,dict(ob)))
                emissions.append(rec); i+=1
            while queue and queue[0][0]<=now:
                arrival,idx,ob=heapq.heappop(queue)
                status=rx.receive(ob,now)
                deliveries.append(dict(packet_index=idx,native_rx_s=arrival,processed_s=now,sequence=ob['sequence'],status=status))
            if step==110:
                audited=rx.available(now)
                advisory=dict(issued_s=now,expires_s=36,road='A',action='detour',claimed_closed=True,text='Road A is closed according to the supplied observation. Road B is available; consider the detour. No travel-time saving is guaranteed.')
                save(out/'request.json',dict(advisory=advisory,evidence=audited))
                if audited is None: result['failure']='evidence_missing_at_predeclared_issue'
                else:
                    messages=[dict(role='system',content=SYSTEM),dict(role='user',content=json.dumps(dict(advisory=advisory,evidence=audited)))]
                    save(out/'messages.json',messages); result['submit_wall_s']=time.monotonic()-origin
                    future=pool.submit(audit,mode,messages)
            pending=future is not None and not future.done()
            if future is not None and future.done() and not handled:
                handled=True; rec=future.result(); save(out/'audit.json',rec)
                decision=consume('content',advisory,rx,now,before_junction=road=='approach',audited=audited,verdict=rec.get('decision'))
                result.update(decision=decision,consume_sim_s=now,consume_wall_s=time.monotonic()-origin,service_s=rec['elapsed_s'],queue_wait_s=rec['started_wall']-origin-result['submit_wall_s'],current_evidence=rx.available(now),audited_evidence=audited,audit_status=rec['status'],audit_decision=rec.get('decision'))
                if decision['admit']:
                    c.vehicle.setRoute('focal',['approach','detour1','detour2','exit']); result['acted']=True
            samples.append(dict(sim_s=now,wall_s=time.monotonic()-origin,road=road,true_closed=closed,pending=pending,received_sequence=rx.current['sequence'] if rx.current else None))
        if future is not None and not handled: result['failure']='audit_unhandled_by_paced_horizon'
        while c.simulation.getMinExpectedNumber() and c.simulation.getTime()<300: c.simulationStep()
    finally:
        c.close(); pool.shutdown(wait=True)
        for name,data in [('observations',observations),('emissions',emissions),('deliveries',deliveries),('samples',samples)]: save(out/(name+'.json'),data)
    trip=next(x for x in ET.parse(out/'trips.xml').getroot() if x.get('id')=='focal')
    result.update(arrived=float(trip.get('arrival'))>=0,travel_duration_s=float(trip.get('duration')),pending_steps=sum(s['pending'] for s in samples),max_pacing_lag_s=max(s['wall_s']-s['sim_s'] for s in samples),max_packet_processing_lag_s=max(d['processed_s']-d['native_rx_s'] for d in deliveries),tx=len(emissions),rx=len(deliveries),lost=sum(not e['received'] for e in emissions),closed_lane_entries=sum(s['true_closed'] and s['road']=='main' for s in samples),status='complete')
    save(out/'result.json',result); print(json.dumps(result),flush=True); return result

def main():
    OUT.mkdir(exist_ok=True)
    with (OUT/'execution.lock').open('a') as lock,(ROOT/'runs/ollama.lock').open('a') as model_lock:
        for f in (lock,model_lock): fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (OUT/'summary.json').exists(): raise SystemExit('Already complete')
        if (OUT/'plan.json').exists(): assert json.loads((OUT/'plan.json').read_text())==PLAN
        else: save(OUT/'plan.json',PLAN)
        with httpx.Client(timeout=5,trust_env=False) as client:
            r=client.get('http://127.0.0.1:11434/api/tags'); r.raise_for_status()
            identity=next(m for m in r.json()['models'] if m['name']==MODEL)
            assert not identity.get('remote_host') and not identity.get('remote_model')
            save(OUT/'model_identity.json',identity)
        path=ROOT/'data/derived/see_parkinglot_6.csv'
        save(OUT/'inputs.json',dict(trace_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),network_sha256=hashlib.sha256((ROOT/'data/derived/network/network.net.xml').read_bytes()).hexdigest()))
        packets=pd.read_csv(path); packets=packets[packets.tx_offset_s<=35].to_dict('records')
        rows=[episode(m,packets) for m in PLAN['modes']]
        save(OUT/'summary.json',dict(plan=PLAN,episodes=rows,model_digest=identity['digest']))
if __name__=='__main__': main()
