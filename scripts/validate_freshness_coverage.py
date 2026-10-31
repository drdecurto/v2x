import json,fcntl
from pathlib import Path
from v2x.credentials import ROOT
from v2x.evidence import EvidenceReceiver,freshness_intervals
O=ROOT/'runs/freshness_coverage_v1';O.mkdir(exist_ok=True)
with (O/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (O/'summary.json').exists():raise SystemExit('Already completed')
 plan={'profiles':[1,6],'window':'first to last recorded transmission, no extrapolation into drain','age_limit_s':5,'measure':'exact time integration using accepted received observations only; initial missing interval counted','verification':'independent 1ms midpoint receiver sweep; bound = two samples per accepted update plus expiry','scope':'single-link offline sensitivity, no auditor or traffic feedback'}
 (O/'plan.json').write_text(json.dumps(plan,indent=2));rows=[]
 for profile in [1,6]:
  p=ROOT/'runs/chronological_replay_v1'/str(profile)
  emissions=[json.loads(x) for x in (p/'emissions.jsonl').read_text().splitlines()];deliveries=[json.loads(x) for x in (p/'deliveries.jsonl').read_text().splitlines()]
  receiver=EvidenceReceiver(5);updates=[]
  for d in deliveries:
   evidence={'source_id':'RSU_0','sequence':d['observation_sequence'],'observed_at_s':d['observed_at_s']}
   decision=receiver.receive(evidence,d['rx_s']);assert decision==d['decision']
   if decision=='updated':updates.append(d)
  start=emissions[0]['tx_s'];end=emissions[-1]['tx_s'];segments,summary=freshness_intervals(updates,start,end,5)
  # Independent sampled observation-only consumer, using all receipts rather than integration cuts.
  rx=EvidenceReceiver(5);j=0;fresh=0;dt=.001;t=start
  while t<end:
   width=min(dt,end-t);mid=t+width/2
   while j<len(deliveries) and deliveries[j]['rx_s']<=mid:
    d=deliveries[j];rx.receive({'source_id':'RSU_0','sequence':d['observation_sequence'],'observed_at_s':d['observed_at_s']},d['rx_s']);j+=1
   if rx.available(mid) is not None:fresh+=width
   t+=width
  error=abs(fresh-summary['fresh']);bound=2*(len(updates)+1)*dt
  assert error<=bound and abs(sum(summary[x] for x in ['fresh','stale','missing'])-(end-start))<1e-8
  summary.update(profile=profile,sampled_fresh_s=fresh,verification_error_s=error,verification_bound_s=bound,accepted_updates=len(updates))
  (O/f'{profile}_intervals.json').write_text(json.dumps(segments,indent=2));rows.append(summary)
 (O/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
