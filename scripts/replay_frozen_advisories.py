"""Controlled response-path replay with measured service times; no live timing claim."""
import bisect,hashlib,json,fcntl
from collections import Counter
from datetime import datetime,timezone
from v2x.credentials import ROOT
from v2x.consumer import consume
from v2x.evidence import EvidenceReceiver
O=ROOT/'runs/frozen_advisory_replay_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  assert not (O/'decisions.json').exists(),'Completed run must not be replaced'
  files=list((ROOT/'runs/advisory_benchmark_v1').glob('*.jsonl'))+list((ROOT/'runs/advisory_structured_local_v1').glob('*.jsonl'))
  files=[p for p in files if not (p.parent.name=='advisory_benchmark_v1' and p.name=='llama3.1_8b.jsonl')]
  cases=json.loads((ROOT/'runs/advisory_benchmark_v1/cases.json').read_text())
  assert cases==json.loads((ROOT/'runs/advisory_structured_local_v1/cases.json').read_text())
  traces={}
  for profile in [1,6]:
   p=ROOT/f'runs/chronological_replay_v1/{profile}/emissions.jsonl';files.append(p);traces[str(profile)]=[json.loads(x) for x in p.read_text().splitlines()]
  plan=dict(created_at=datetime.now(timezone.utc).isoformat(),stage='exploratory_offline_response_path_sensitivity',profiles=['ideal','1','6'],soft_timeout_s=2,hard_deadline_s=5,evidence_age_limit_s=5,policies=['none','rules','content','deadline'],initial_evidence='All arms begin with the exact benchmark observation already available at the auditor/consumer. No observation-refresh process; stale cases remain stale. Conditional on initial receipt, not full V2X exchange.',route='Map each case road to A; choose main if observed open, detour if closed; structured claimed_closed equals evidence. Prose contradictions are not silently parsed into structured fields. No vehicle controls executed.',timing='Measured client duration used as event duration, no extra inference. Deadline emits returned verdict before2s or template at2s on pending/failure; content withholds at5s if incomplete. This is simulated timer replay, not a new live asynchronous experiment.',transport='Every arm uses first native TX at/after message ready. One packet, no retries, receive delay/loss preserved. Baselines transmit at0 readiness; content/timeout at their readiness. Hard5s application deadline and evidence expiry rechecked at delivery. Native offered load is a replay abstraction, not generated network performance.',alignment='Request trace epoch 10+6*world+wording seconds (absolute in stored trace); same for all categories/models/policies. Isolated case replay, not simultaneous load. No looping/resampling.',scope='Two reused stationary LTE traces, no city coupling, no urban/5G/6G validation. No independent packet/model/case population inference.',cases=180,models=6,expected_decisions=12960)
  save(O/'plan.json',plan)
  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
  for p in [ROOT/'runs/advisory_benchmark_v1/cases.json',ROOT/'scripts/replay_frozen_advisories.py',ROOT/'src/v2x/consumer.py',ROOT/'src/v2x/evidence.py',ROOT/'src/v2x/policy.py',O/'plan.json']:inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
  save(O/'inputs.json',inputs);out=[]
  for p in files[:6]:
   responses={r['id']:r for r in map(json.loads,p.read_text().splitlines())};assert len(responses)==180
   for case in cases:
    rec=responses[case['id']];elapsed=rec['elapsed_s'];age=case['evaluation_time_s']-case['evidence']['observed_at_s'];closed=case['evidence']['road_closed'];epoch=10+6*case['world']+int(case['id'][-1])
    obs=dict(source_id='frozen_benchmark',sequence=1,observed_at_s=-age,road_A_closed=closed,road_B_available=True)
    advisory=dict(issued_s=0,expires_s=5,road='A',action='detour' if closed else 'main',claimed_closed=closed,text=case['advisory'])
    for profile in plan['profiles']:
     for policy in plan['policies']:
      fallback=False;ready=0;verdict=None;timeout=False
      if policy=='content':ready=min(elapsed,5);timeout=elapsed>=5;verdict=rec.get('decision') if not timeout and rec['status']=='ok' else None
      if policy=='deadline':
       ready=min(elapsed,2);fallback=elapsed>=2 or rec['status']!='ok';verdict=rec.get('decision') if not fallback else None
      arrival=ready;packet=None;reason=None
      if timeout:reason='service_deadline'
      elif profile!='ideal':
       trace=traces[profile];index=bisect.bisect_left([x['tx_s'] for x in trace],epoch+ready)
       if index==len(trace):reason='trace_exhausted'
       else:
        packet=trace[index]['packet_index']
        if not trace[index]['received']:reason='packet_lost'
        else:arrival=trace[index]['rx_s']-epoch
      if reason:decision=dict(admit=False,text=False,mode=reason,action=None)
      else:
       rx=EvidenceReceiver(5);rx.receive(obs,0)
       decision=consume(policy,advisory,rx,arrival,before_junction=arrival<5,audited=obs,verdict=verdict,deadline_fallback=fallback)
      out.append(dict(model=rec['model'],provider=rec['provider'],id=case['id'],world=case['world'],category=case['category'],expected=case['expected'],profile=profile,policy=policy,service_s=elapsed,ready_s=ready,delivery_s=arrival if reason is None else None,trace_epoch_s=epoch,packet_index=packet,fallback=fallback,decision=decision))
  assert len(out)==12960
  summary=[]
  for model in sorted({r['model'] for r in out}):
   for profile in plan['profiles']:
    for policy in plan['policies']:
     rr=[r for r in out if (r['model'],r['profile'],r['policy'])==(model,profile,policy)]
     summary.append(dict(model=model,profile=profile,policy=policy,n=len(rr),clean_n=30,clean_admitted=sum(r['category']=='clean' and r['decision']['admit'] for r in rr),rejected_reference_texts_delivered=sum(r['expected']=='reject' and r['decision']['text'] for r in rr),uncertain_texts_delivered=sum(r['expected']=='unsure' and r['decision']['text'] for r in rr),stale_admitted=sum(r['category']=='stale' and r['decision']['admit'] for r in rr),modes=dict(Counter(r['decision']['mode'] for r in rr))))
  save(O/'decisions.json',out);save(O/'summary.json',summary);print('Saved',len(out),'paired policy records')
if __name__=='__main__':main()
