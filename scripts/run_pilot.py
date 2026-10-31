import json,fcntl
from v2x.credentials import ROOT
from v2x.simulation import run_episode
cfg=json.loads((ROOT/'config/pilot.json').read_text())
messages=json.loads((ROOT/'data/derived/development_messages.json').read_text())
profiles={r['id']:r for r in map(json.loads,(ROOT/'runs/nebius_development.jsonl').read_text().splitlines()) if r['status']=='ok'}
# Four deliberately selected development cases, not an estimate of natural prevalence.
selected=[r for r in messages if r['repetition']==0 and r['case'] in ('clean_closed','clean_open','false_closure','unsupported_guarantee')]
root=ROOT/'runs/pilot_v1';root.mkdir(exist_ok=True)
with (root/'runner.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for row in selected:
        profile=profiles[row['id']]
        for condition in ('instant','see_1470','synthetic_5s'):
            for seed in cfg['seeds']:
                for policy in cfg['policies']:
                    path=root/f'{row["case"]}_{condition}_{seed}_{policy}'
                    if (path/'result.json').exists():continue
                    r=run_episode(row,policy,seed,condition,profile['decision'],profile['elapsed_s'],path)
                    print(path.name,round(r['travel_duration_s'],2),'arrived',r['arrived'],flush=True)
    results=[json.loads(p.read_text()) for p in sorted(root.glob('*/result.json'))]
    (ROOT/'reports/pilot_results.json').write_text(json.dumps(results,indent=2))
    print('Completed',len(results),'development episodes',flush=True)
