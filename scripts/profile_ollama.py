"""Profile an already-installed local model; refuse cloud aliases."""
import json,time,hashlib,fcntl,argparse
from datetime import datetime,timezone
import httpx
from v2x.credentials import ROOT
from profile_nebius import SYSTEM

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',default='qwen2.5:14b');args=parser.parse_args();model=args.model
    tag=model.replace(':','_').replace('/','_')
    rows=json.loads((ROOT/'data/derived/development_messages.json').read_text())
    out=ROOT/f'runs/ollama_{tag}_development.jsonl'
    with (ROOT/'runs/ollama.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        done={r['id'] for r in map(json.loads,out.read_text().splitlines())} if out.exists() else set()
        with httpx.Client(base_url='http://127.0.0.1:11434',timeout=120,trust_env=False) as client:
            tags=client.get('/api/tags').json()['models']
            identity=next(t for t in tags if t['name']==model)
            if identity.get('remote_host') or identity.get('remote_model'):raise ValueError('Cloud model is not a local measurement')
            meta={'model':model,'digest':identity['digest'],'details':identity['details'],'version':client.get('/api/version').json()}
            (ROOT/f'reports/ollama_{tag}_identity.json').write_text(json.dumps(meta,indent=2))
            for row in rows:
                if row['id'] in done:continue
                messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'advisory':row['advisory'],'evidence':row['evidence']})}]
                rec={'id':row['id'],'model':model,'digest':meta['digest'],'started_at':datetime.now(timezone.utc).isoformat(),'status':'error','prompt_sha256':hashlib.sha256(json.dumps(messages).encode()).hexdigest()}
                start=time.perf_counter()
                try:
                    r=client.post('/api/chat',json={'model':model,'messages':messages,'stream':False,'keep_alive':'5m','options':{'temperature':0,'num_predict':160,'num_ctx':2048,'seed':42}})
                    rec['http_status']=r.status_code
                    if r.status_code==200:
                        data=r.json();content=data['message']['content']
                        rec.update(response=content,server_metrics={k:data.get(k) for k in ('total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration','done_reason')})
                        parsed=json.loads(content.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip())
                        if parsed.get('decision') not in ('accept','reject','unsure'):raise ValueError('Invalid decision')
                        rec.update(status='ok',decision=parsed['decision'])
                except (httpx.HTTPError,ValueError,KeyError) as e:rec['error_type']=type(e).__name__
                rec['elapsed_s']=time.perf_counter()-start
                with out.open('a') as f:f.write(json.dumps(rec)+'\n');f.flush()
                print(row['id'],rec['status'],round(rec['elapsed_s'],3),flush=True)
                if rec.get('http_status') not in (200,):break
            processes=client.get('/api/ps').json()
            (ROOT/f'reports/ollama_{tag}_loaded_models.json').write_text(json.dumps(processes,indent=2))
if __name__=='__main__':main()
