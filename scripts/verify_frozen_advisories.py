"""Independent event arithmetic and source-file verification; does not call consumer."""
import bisect,hashlib,json
from collections import Counter
from v2x.credentials import ROOT
O=ROOT/'runs/frozen_advisory_replay_v1'
def main():
 inputs=json.loads((O/'inputs.json').read_text())
 for p,h in inputs.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 cases={r['id']:r for r in json.loads((ROOT/'runs/advisory_benchmark_v1/cases.json').read_text())}
 records=json.loads((O/'decisions.json').read_text());assert len(records)==12960;assert len({(r['model'],r['id'],r['profile'],r['policy']) for r in records})==len(records)
 traces={str(i):[json.loads(x) for x in (ROOT/f'runs/chronological_replay_v1/{i}/emissions.jsonl').read_text().splitlines()] for i in [1,6]}
 raw={}
 for folder in ['advisory_benchmark_v1','advisory_structured_local_v1']:
  for p in (ROOT/'runs'/folder).glob('*.jsonl'):
   rr=[json.loads(x) for x in p.read_text().splitlines()]
   if len(rr)==180:raw.update({(r['model'],r['id']):r for r in rr})
 baseline={}
 for r in records:
  c=cases[r['id']];call=raw[(r['model'],r['id'])];policy=r['policy'];elapsed=call['elapsed_s']
  assert r['service_s']==elapsed
  ready=0 if policy in ['none','rules'] else min(elapsed,5 if policy=='content' else 2)
  assert ready==r['ready_s'];reason=None;at=ready
  if policy=='content' and elapsed>=5:reason='service_deadline'
  elif r['profile']!='ideal':
   t=traces[r['profile']];j=bisect.bisect_left([x['tx_s'] for x in t],r['trace_epoch_s']+ready)
   if j==len(t):reason='trace_exhausted'
   else:
    assert r['packet_index']==t[j]['packet_index']
    if not t[j]['received']:reason='packet_lost'
    else:at=t[j]['rx_s']-r['trace_epoch_s']
  age=c['evaluation_time_s']-c['evidence']['observed_at_s']
  if reason is None:
   if at>=5:reason='invalid_or_expired'
   elif age+at>5:reason='evidence_unavailable'
   elif policy=='none':reason='unchecked'
   elif policy=='rules' or (policy=='deadline' and (elapsed>=2 or call['status']!='ok')):reason='verified_template'
   else:reason='content_accept' if call.get('decision')=='accept' else 'content_'+str(call.get('decision'))
  assert r['decision']['mode']==reason,(r,reason)
  assert r['decision']['admit']==(reason in ['unchecked','verified_template','content_accept'])
  assert r['decision']['text']==(reason in ['unchecked','content_accept'])
  if c['category']=='stale':assert not r['decision']['admit']
  if policy in ['none','rules']:
   key=(r['id'],r['profile'],policy)
   if key in baseline:assert baseline[key]==r['decision']
   baseline[key]=r['decision']
 for s in json.loads((O/'summary.json').read_text()):
  rr=[r for r in records if (r['model'],r['profile'],r['policy'])==(s['model'],s['profile'],s['policy'])];assert len(rr)==s['n']==180
  assert s['modes']==dict(Counter(r['decision']['mode'] for r in rr))
 city=ROOT/'runs/paired_city_stress_v1';n=0
 for a in (city/'no_diversion').glob('*/*/result.json'):
  rel=a.parent.relative_to(city/'no_diversion');b=city/'full_diversion'/rel
  assert hashlib.sha256((a.parent/'routes.xml').read_bytes()).digest()==hashlib.sha256((b/'routes.xml').read_bytes()).digest()
  none=json.loads(a.read_text());full=json.loads((b/'result.json').read_text());assert none['applied']==0;assert full['applied']<=full['eligible'];n+=1
 assert n==60
 (O/'verification.json').write_text(json.dumps(dict(source_hashes=len(inputs),independently_verified_policy_records=len(records),matched_route_files=n,all_stale_blocked=True,baseline_invariance=True),indent=2))
 print('Verified',len(records),'policy records and',n,'matched traffic route inputs')
if __name__=='__main__':main()
