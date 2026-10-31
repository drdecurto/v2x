"""Fixed Phi-4 replication; shared city engine, native JSON, no paid requests."""
import argparse,fcntl,hashlib,json,shutil,time
from datetime import datetime,timezone
from pathlib import Path
import httpx
import city_policy_bridge as bridge
from v2x.credentials import ROOT
O=ROOT/'runs/city_policy_local_v1';MODEL='phi4:latest'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def prepare():
 assert not O.exists();O.mkdir();source=ROOT/'runs/city_policy_bridge_v1'
 for name in ['cases.json','assignments.json']:shutil.copy2(source/name,O/name)
 plan=json.loads((source/'plan.json').read_text());plan.update(created_at=datetime.now(timezone.utc).isoformat(),model=MODEL,stage='prospectively_frozen_local_model_replication_known_development_blocks',planned_paid_calls=0,max_tokens=256,local_options=dict(temperature=0,num_predict=256,num_ctx=2048,seed=42,format='json',keep_alive='5m'),reason='Primary remote timings all below0.85s; no timeout arm activation. InstalledPhi4 tests timeout under actual measured local service duration. This is not a same-model placement comparison.',semantic_audit='360offline local Phi4 audits using exactly the prior prompt/cases. NativeJSON,256outputtokens,2048context,seed42. Exact digest recorded; cold start retained. Measured durations replayed in SUMO; no live per-vehicle inference or queue/load claim.',baseline_reuse='Reuse120exact prior none/rules arms because these ignore verdict and service duration. Source provenance/hashes retained. Only120new content/deadline runs; reused arms are not independent observations.')
 save(O/'plan.json',plan);inputs=json.loads((source/'inputs.json').read_text());inputs={p:h for p,h in inputs.items() if not p.startswith('runs/city_policy_bridge_v1/')}
 for p in [O/'plan.json',O/'cases.json',O/'assignments.json',Path(__file__)]:inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 save(O/'inputs.json',inputs)
 for city in plan['cities']:
  for seed in plan['seeds']:
   for policy in ['none','rules']:
    src=source/city/str(seed)/policy;dst=O/city/str(seed)/policy;shutil.copytree(src,dst)
    save(dst/'reuse.json',dict(source=str(src.relative_to(ROOT)),reason='No content audit/template decisions have zero service readiness and ignore model verdict.',hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir() if p.is_file()}))
 print('Frozen local replication;120baseline arms reused,120new arms planned')
def audit():
 bridge.O=O;bridge.check();target=O/'audits.jsonl'
 with (ROOT/'runs/ollama.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  with httpx.Client(timeout=60,trust_env=False) as client:
   tags=client.get('http://127.0.0.1:11434/api/tags').json()['models'];identity=next(x for x in tags if x['name']==MODEL);assert not identity.get('remote_host') and not identity.get('remote_model');save(O/'identity.json',identity)
   done={r['id'] for r in map(json.loads,target.read_text().splitlines())} if target.exists() else set();bad=0
   for case in json.loads((O/'cases.json').read_text()):
    if case['id'] in done:continue
    marker=O/'started'/case['id'];marker.parent.mkdir(exist_ok=True);assert not marker.exists(),'Interrupted local call needs review';marker.write_text(datetime.now(timezone.utc).isoformat())
    messages=[dict(role='system',content=bridge.SYSTEM),dict(role='user',content=json.dumps({k:case[k] for k in ['advisory','evidence']}))]
    rec=dict(id=case['id'],model=MODEL,digest=identity['digest'],status='error',started_at=datetime.now(timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(json.dumps(messages).encode()).hexdigest());start=time.perf_counter()
    try:
     r=client.post('http://127.0.0.1:11434/api/chat',json=dict(model=MODEL,messages=messages,stream=False,format='json',keep_alive='5m',options=dict(temperature=0,num_predict=256,num_ctx=2048,seed=42)));rec['http_status']=r.status_code
     if r.status_code==200:
      d=r.json();content=d['message']['content'];rec.update(response=content,served_model=d.get('model'),server_metrics={k:d.get(k) for k in ['total_duration','load_duration','eval_count','eval_duration']})
      v=json.loads(content)['decision'];assert v in ['accept','reject','unsure'];rec.update(status='ok',decision=v)
    except (httpx.HTTPError,ValueError,KeyError,AssertionError) as e:rec['error_type']=type(e).__name__
    rec['elapsed_s']=time.perf_counter()-start
    with target.open('a') as f:f.write(json.dumps(rec)+'\n');f.flush()
    print(case['id'],rec['status'],round(rec['elapsed_s'],3),flush=True);bad=bad+1 if rec['status']!='ok' else 0
    if rec.get('http_status') in [401,403,429] or bad>=3:raise RuntimeError('Local configuration failed; records retained')
 save(O/'audits_complete.json',dict(count=360,at=datetime.now(timezone.utc).isoformat()))
def simulate():
 bridge.O=O;bridge.MODEL=MODEL;bridge.simulate()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','audit','simulate']);a=p.parse_args();{'prepare':prepare,'audit':audit,'simulate':simulate}[a.mode]()
