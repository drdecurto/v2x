import json,hashlib
from collections import Counter
from v2x.credentials import ROOT
O=ROOT/'runs/prospective_timeout_v1';plan=json.loads((O/'plan.json').read_text());freeze=json.loads((O/'freeze.json').read_text());assert freeze['plan_sha256']==hashlib.sha256((O/'plan.json').read_bytes()).hexdigest();assert freeze['runner_sha256']==hashlib.sha256((ROOT/'scripts/run_prospective_timeout.py').read_bytes()).hexdigest()
rows=[]
for model in plan['models']:
 for case in plan['fixtures']:
  p=O/model.replace(':','_')/case['id'];r=json.loads((p/'result.json').read_text());assert r['model']==model and r['case']==case;assert r['digest']==json.loads((p/'started.json').read_text())['digest'];assert r['drained_s']>=r['inference']['service_s'];assert set(r['decisions'])==set(plan['policies'])
  for policy,record in r['decisions'].items():
   d=record['decision'];now=record['at_s'];assert now>=0
   if not d['admit']:assert not d['text']
   if d['mode']=='verified_template':assert not d['text']
   if policy=='content' and record['hard_timeout']:assert not d['admit']
   if policy=='deadline' and record['soft_timeout']:assert not d['text']
   if case['condition']=='stale' and now>.5:assert not d['admit']
   if case['condition'] in ['expired','choice_passed'] and now>=1:assert not d['admit']
   if case['condition']=='superseded' and now>=1 and policy=='content':assert not d['admit']
  rows.append(r)
summary=[]
for model in plan['models']:
 rr=[r for r in rows if r['model']==model];stable=[r for r in rr if r['case']['condition']=='stable'];assert Counter(r['case']['label'] for r in stable)=={'clean':3,'violating':6,'unsure':3}
 for policy in plan['policies']:
  summary.append(dict(model=model,policy=policy,stable_cases=12,clean_admitted=sum(r['case']['label']=='clean' and r['decisions'][policy]['decision']['admit'] for r in stable),violating_texts=sum(r['case']['label']=='violating' and r['decisions'][policy]['decision']['text'] for r in stable),uncertain_admitted=sum(r['case']['label']=='unsure' and r['decisions'][policy]['decision']['admit'] for r in stable),modes=dict(Counter(r['decisions'][policy]['decision']['mode'] for r in rr)),max_decision_s=max(r['decisions'][policy]['at_s'] for r in rr)))
result=dict(verified=True,calls=len(rows),parse_success=sum(r['inference']['status']=='ok' for r in rows),summary=summary,timing_cases=[dict(model=r['model'],case=r['case']['id'],decisions=r['decisions']) for r in rows if r['case']['condition']!='stable'])
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='timing_cases'},indent=2))
