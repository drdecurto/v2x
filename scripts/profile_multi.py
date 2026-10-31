"""Cross-family development measurements with a shared, locked budget ledger."""
import json,time,hashlib,fcntl
from datetime import datetime,timezone
import httpx
from v2x.credentials import ROOT,credentials
from profile_nebius import SYSTEM

def main():
    cfg=json.loads((ROOT/'config/pilot.json').read_text())
    rows=json.loads((ROOT/'data/derived/development_messages.json').read_text())
    roster=[('openai/gpt-oss-120b',{'reasoning_effort':'low'}),('nvidia/nemotron-3-super-120b-a12b',{})]
    # Matching output budget includes reasoning for reasoning models; incomplete outputs remain failures.
    max_tokens=1024
    ledger=ROOT/'runs/api_reservations.jsonl';out=ROOT/'runs/nebius_multimodel_development.jsonl'
    with (ROOT/'runs/nebius.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        done={(r['model'],r['id']) for r in map(json.loads,out.read_text().splitlines())} if out.exists() else set()
        prior=list(map(json.loads,ledger.read_text().splitlines())) if ledger.exists() else []
        base,key=credentials()
        with httpx.Client(timeout=60,follow_redirects=False,trust_env=False) as client:
            for model,extra in roster:
                for row in rows:
                    if (model,row['id']) in done:continue
                    messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'advisory':row['advisory'],'evidence':row['evidence']})}]
                    reserve=((len(json.dumps(messages).encode())+200)*3+max_tokens*15)/1e6
                    if len(prior)>=cfg['max_live_calls_total'] or sum(x['reserved_usd'] for x in prior)+reserve>cfg['max_reserved_usd_total']:raise SystemExit('Project budget reached')
                    at=datetime.now(timezone.utc).isoformat()
                    monthly=sum(x['reserved_usd'] for x in prior if x['at'][:7]==at[:7])
                    if monthly+reserve>cfg['monthly_project_ceiling_usd']:raise SystemExit('Monthly project ceiling reached')
                    reservation={'id':row['id'],'model':model,'reserved_usd':reserve,'at':at}
                    with ledger.open('a') as f:f.write(json.dumps(reservation)+'\n');f.flush()
                    prior.append(reservation)
                    payload={'model':model,'messages':messages,'temperature':0,'max_tokens':max_tokens,**extra}
                    rec={'id':row['id'],'model':model,'started_at':at,'max_tokens':max_tokens,'extra_parameters':extra,'status':'error','prompt_sha256':hashlib.sha256(json.dumps(messages).encode()).hexdigest()}
                    start=time.perf_counter()
                    try:
                        r=client.post(base+'chat/completions',headers={'Authorization':'Bearer '+key},json=payload)
                        rec['http_status']=r.status_code
                        if r.status_code==200:
                            d=r.json();content=d['choices'][0]['message'].get('content') or ''
                            rec.update(response=content,served_model=d.get('model'),usage=d.get('usage'),finish_reason=d['choices'][0].get('finish_reason'))
                            parsed=json.loads(content.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip())
                            if parsed.get('decision') not in ('accept','reject','unsure'):raise ValueError('Invalid decision')
                            rec.update(status='ok',decision=parsed['decision'])
                    except (httpx.HTTPError,ValueError,KeyError,IndexError) as e:rec['error_type']=type(e).__name__
                    rec['elapsed_s']=time.perf_counter()-start
                    with out.open('a') as f:f.write(json.dumps(rec)+'\n');f.flush()
                    print(model,row['id'],rec['status'],round(rec['elapsed_s'],3),flush=True)
                    if rec.get('http_status') in (401,403,429):return
                    # Stop a persistently incompatible configuration; retain errors rather than optimize invisibly.
                    recent=[json.loads(x) for x in out.read_text().splitlines() if json.loads(x)['model']==model][-3:]
                    if len(recent)==3 and all(x['status']!='ok' for x in recent):break
if __name__=='__main__':main()
