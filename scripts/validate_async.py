"""Three bounded development bridge episodes; 40 s real-time window, then fast drain.

No remote API requests. Fixed-latency arms validate scheduling, not model quality.
"""
import concurrent.futures,fcntl,hashlib,json,time
from pathlib import Path
import xml.etree.ElementTree as ET
import httpx,traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure,freshness_reason
from profile_nebius import SYSTEM
OUT=ROOT/'runs/async_validation_v1'
MODEL='qwen2.5:14b'

def audit(mode,messages):
    start=time.monotonic();rec={'mode':mode,'started_wall':start,'status':'error'}
    try:
        if mode!='ollama':
            time.sleep(2 if mode=='fixed_2s' else 9)
            rec.update(status='ok',decision='accept',synthetic=True)
        else:
            with httpx.Client(timeout=25,trust_env=False) as client:
                response=client.post('http://127.0.0.1:11434/api/chat',json={'model':MODEL,'messages':messages,'stream':False,'keep_alive':'5m','options':{'temperature':0,'num_predict':160,'num_ctx':2048,'seed':42}})
                response.raise_for_status();data=response.json();content=data['message']['content']
                rec.update(response=content,server_metrics={k:data.get(k) for k in ['total_duration','load_duration','prompt_eval_duration','eval_duration','eval_count']})
                parsed=json.loads(content.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip())
                if parsed.get('decision') not in ('accept','reject','unsure'):raise ValueError('Invalid decision')
                rec.update(status='ok',decision=parsed['decision'],synthetic=False)
    except (httpx.HTTPError,ValueError,KeyError) as exc:rec['error_type']=type(exc).__name__
    rec['finished_wall']=time.monotonic();rec['elapsed_s']=rec['finished_wall']-start
    return rec

def episode(mode):
    out=OUT/mode;out.mkdir(exist_ok=True)
    if (out/'result.json').exists():return json.loads((out/'result.json').read_text())
    (out/'routes.xml').write_text('<routes><vType id="car" vClass="passenger" accel="2.6" decel="4.5" sigma="0.5"/><route id="direct" edges="approach main exit"/><vehicle id="focal" type="car" route="direct" depart="0" departSpeed="max"/></routes>')
    traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(out/'routes.xml'),'--seed','3101','--step-length','0.2','--no-step-log','true','--duration-log.disable','true','--time-to-teleport','-1','--tripinfo-output',str(out/'trips.xml'),'--tripinfo-output.write-unfinished','true','--error-log',str(out/'errors.log')],label='async',numRetries=3)
    c=traci.getConnection('async');closure=LaneClosure('main_0');pool=concurrent.futures.ThreadPoolExecutor(max_workers=1)
    origin=time.monotonic();future=None;handled=False;events=[];samples=[];lags=[];pending_steps=0;observed={'observed_s':0,'version':0,'road_A_closed':False,'road_B_available':True};closed=False;reopened=False;updated=False
    result={'mode':mode,'seed':3101,'paced_window_s':40,'issue_s':8,'reopen_s':12,'observation_delivery_s':14,'observation_delay_s':2,'acted':False,'status':'incomplete'}
    try:
        while c.simulation.getTime()<220 and c.simulation.getMinExpectedNumber():
            before=c.simulation.getTime();target=before+.2
            if target<=40+1e-8:time.sleep(max(0,origin+target-time.monotonic()))
            c.simulationStep();now=c.simulation.getTime();wall=time.monotonic()-origin
            if now<=40+1e-8:lags.append(wall-now)
            if now>=5 and not closed:
                closure.close(c);closed=True;observed={'observed_s':now,'version':1,'road_A_closed':True,'road_B_available':True};events.append({'sim_s':now,'event':'closure_and_initial_observation'})
            if now>=12 and not reopened:
                closure.reopen(c);reopened=True;events.append({'sim_s':now,'event':'authoritative_reopening'})
            if now>=14 and not updated:
                observed={'observed_s':12,'version':2,'road_A_closed':False,'road_B_available':True};updated=True;events.append({'sim_s':now,'event':'reopening_observation_received'})
            ids=c.vehicle.getIDList();road=c.vehicle.getRoadID('focal') if 'focal' in ids else None
            if closure.active:assert road!='main'
            if now>=8 and future is None:
                advisory={'road':'A','action':'detour','claimed_closed':True,'issued_s':now,'expires_s':38,'text':'Road A is closed. Road B is available; consider the detour. No travel-time saving is guaranteed.'}
                audited=dict(observed);messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'advisory':advisory,'evidence':audited})}]
                (out/'request.json').write_text(json.dumps({'advisory':advisory,'evidence':audited,'messages':messages},indent=2))
                result['submit_wall_s']=time.monotonic()-origin;future=pool.submit(audit,mode,messages);events.append({'sim_s':now,'event':'audit_submitted'})
            if future is not None and not future.done():pending_steps+=1
            if future is not None and future.done() and not handled:
                handled=True;rec=future.result();(out/'audit.json').write_text(json.dumps(rec,indent=2))
                reason=freshness_reason(advisory,audited,observed,now,30,road=='approach')
                result.update(audit_status=rec['status'],audit_decision=rec.get('decision'),service_s=rec['elapsed_s'],decision_sim_s=now,decision_wall_s=wall,freshness_reason=reason,queue_wait_s=rec['started_wall']-origin-result['submit_wall_s'])
                if reason is None and rec.get('decision')=='accept':
                    c.vehicle.setRoute('focal',['approach','detour1','detour2','exit']);result['acted']=True
                events.append({'sim_s':now,'event':'audit_consumed','reason':reason,'acted':result['acted']})
            samples.append({'sim_s':now,'wall_s':wall,'road':road,'pending':future is not None and not future.done(),'phase':'paced' if now<=40+1e-8 else 'fast_drain','observed_version':observed['version']})
            if now>=40 and not handled:raise RuntimeError('Audit incomplete at end of paced window')
    finally:c.close();pool.shutdown(wait=True)
    trip=next(x for x in ET.parse(out/'trips.xml').getroot() if x.get('id')=='focal')
    result.update(status='complete',arrived=float(trip.get('arrival'))>=0,travel_duration_s=float(trip.get('duration')),pending_simulation_steps=pending_steps,max_pacing_lag_s=max(lags),events=events)
    assert result['arrived'] and pending_steps>0
    if mode=='fixed_2s':assert result['acted'] and result['freshness_reason'] is None
    if mode=='fixed_9s':assert not result['acted'] and result['freshness_reason']=='evidence_version_changed'
    (out/'samples.json').write_text(json.dumps(samples));(out/'result.json').write_text(json.dumps(result,indent=2));print(mode,result['status'],round(result['service_s'],3),result['freshness_reason'],flush=True)
    return result

def main():
    OUT.mkdir(exist_ok=True)
    with (OUT/'execution.lock').open('a') as stage_lock,(ROOT/'runs/ollama.lock').open('a') as inference_lock:
        for lock in (stage_lock,inference_lock):fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with httpx.Client(timeout=5,trust_env=False) as client:
            tags=client.get('http://127.0.0.1:11434/api/tags').json()['models'];identity=next(t for t in tags if t['name']==MODEL)
            assert not identity.get('remote_host') and not identity.get('remote_model')
            (OUT/'model_identity.json').write_text(json.dumps(identity,indent=2))
        rows=[episode(mode) for mode in ('fixed_2s','fixed_9s','ollama')]
        (ROOT/'reports/async_validation.json').write_text(json.dumps({'stage':'development_bridge_not_confirmatory','episodes':rows,'local_model':MODEL,'digest':identity['digest'],'remote_calls':0,'limitations':'Single seed and single advisory per episode; 40-second paced window then accelerated trip completion. Synthetic two-second evidence-update delay, no radio trace in these episodes. No placement or policy-effectiveness conclusion.'},indent=2))
if __name__=='__main__':main()
