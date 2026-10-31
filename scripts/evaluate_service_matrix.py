"""Paired development service replay; measured timing, no new radio/traffic claims."""
import json,hashlib,fcntl
from collections import Counter
from v2x.credentials import ROOT
from v2x.consumer import consume
from v2x.evidence import EvidenceReceiver
O=ROOT/'runs/service_matrix_v1'
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  plan=dict(stage='development_service_replay_not_confirmatory',budgets_s=[.5,2,5,15],policies=['none','rules','content','deadline'],fixtures='Existing eight constructed cases, three repetitions; not24independent language cases',models=['Qwen/Qwen3-30B-A3B-Instruct-2507','openai/gpt-oss-120b','nvidia/nemotron-3-super-120b-a12b','qwen2.5:14b','phi4:latest','llama3.1:8b'],timing='Recorded sequential request elapsed time; no simulated network delay, no queue/load or concurrent hardware inference claim',freshness='Single fixed received observation with age limit60s, stable for diagnostic; isolates audit timing from freshness',deadline='Oracle replay knows completed elapsed time; fallback when greater than budget, not a deployable latency predictor',reference='Constructed labels; qualified-clean versus unsure boundary not human-validated')
  if (O/'plan.json').exists():assert json.loads((O/'plan.json').read_text())==plan
  else:(O/'plan.json').write_text(json.dumps(plan,indent=2))
  files=['nebius_development.jsonl','nebius_multimodel_development.jsonl','ollama_qwen2.5_14b_development.jsonl','ollama_phi4_latest_development.jsonl','ollama_llama3.1_8b_development.jsonl'];records=[];hashes={}
  for name in files:
   p=ROOT/'runs'/name;hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest();records+=list(map(json.loads,p.read_text().splitlines()))
  fixtures={x['id']:x for x in json.loads((ROOT/'data/derived/development_messages.json').read_text())};output=[]
  for model in plan['models']:
   rr=[x for x in records if x.get('model')==model];assert len(rr)==24,(model,len(rr));assert len({x['id'] for x in rr})==24
   for rec in rr:
    f=fixtures[rec['id']];obs=dict(source_id='fixed_fixture',sequence=1,observed_at_s=10,road_A_closed=f['evidence']['road_A_closed'],road_B_available=f['evidence']['road_B_available']);ad=dict(f['advisory'])
    for budget in plan['budgets_s']:
     now=10+budget;rx=EvidenceReceiver(60);rx.receive(obs,10)
     late=rec['elapsed_s']>budget;verdict=rec.get('decision') if rec['status']=='ok' and not late else None
     for policy in plan['policies']:
      fallback=late or rec['status']!='ok'
      decision=consume(policy,ad,rx,now,before_junction=True,audited=obs if verdict else None,verdict=verdict,deadline_fallback=fallback)
      output.append(dict(model=model,id=rec['id'],case=f['case'],reference=f['reference']['label'],budget_s=budget,policy=policy,elapsed_s=rec['elapsed_s'],late=late,decision=decision,violating_original_text_delivered=decision['text'] and f['reference']['label']=='violating',clean_action_admitted=decision['admit'] and f['reference']['label']=='clean'))
  summary=[]
  for model in plan['models']:
   for budget in plan['budgets_s']:
    for policy in plan['policies']:
     rows=[r for r in output if (r['model'],r['budget_s'],r['policy'])==(model,budget,policy)];summary.append(dict(model=model,budget_s=budget,policy=policy,n=len(rows),clean_n=sum(r['reference']=='clean' for r in rows),violating_n=sum(r['reference']=='violating' for r in rows),clean_actions=sum(r['clean_action_admitted'] for r in rows),violating_texts=sum(r['violating_original_text_delivered'] for r in rows),admitted=sum(r['decision']['admit'] for r in rows),modes=dict(Counter(r['decision']['mode'] for r in rows))))
  for name,data in [('inputs',hashes),('decisions',output),('summary',summary)]: (O/(name+'.json')).write_text(json.dumps(data,indent=2))
  print('Completed',len(output),'paired diagnostic decisions')
if __name__=='__main__':main()
