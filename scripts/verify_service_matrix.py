import json,hashlib
from collections import Counter
from v2x.credentials import ROOT
p=ROOT/'runs/service_matrix_v1';rows=json.loads((p/'decisions.json').read_text());summary=json.loads((p/'summary.json').read_text());plan=json.loads((p/'plan.json').read_text())
assert len(rows)==6*24*4*4 and len(summary)==6*4*4
for name,h in json.loads((p/'inputs.json').read_text()).items():assert hashlib.sha256((ROOT/'runs'/name).read_bytes()).hexdigest()==h
assert len({(r['model'],r['id'],r['budget_s'],r['policy']) for r in rows})==len(rows)
for s in summary:
 rr=[r for r in rows if (r['model'],r['budget_s'],r['policy'])==(s['model'],s['budget_s'],s['policy'])]
 assert len(rr)==24 and Counter(r['reference'] for r in rr)=={'clean':9,'violating':12,'unsure':3}
 assert s['clean_actions']==sum(r['reference']=='clean' and r['decision']['admit'] for r in rr)
 assert s['violating_texts']==sum(r['reference']=='violating' and r['decision']['text'] for r in rr)
 assert s['admitted']==sum(r['decision']['admit'] for r in rr)
 for r in rr:
  assert r['late']==(r['elapsed_s']>r['budget_s'])
  if r['policy']=='content' and r['late']:assert not r['decision']['admit']
  if r['decision']['mode']=='verified_template':assert not r['decision']['text']
  if not r['decision']['admit']:assert not r['decision']['text']
(p/'verification.json').write_text(json.dumps(dict(passed=True,decisions=len(rows),summary_rows=len(summary),independent_semantic_cases=8,scope='Input hashes, complete pairing, denominator and decision-record invariants; not human label validation'),indent=2));print('Service records verified')
