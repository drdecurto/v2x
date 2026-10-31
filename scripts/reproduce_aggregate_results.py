"""Recompute manuscript city contrasts from released per-run aggregate summaries.
No raw traces, API credentials, inference or SUMO execution are needed.
"""
from pathlib import Path
import json
import random,statistics
ROOT=Path(__file__).resolve().parents[1]
def main():
 output={}
 for study in ['city_policy_bridge_v1','city_policy_local_v1']:
  rows=json.loads((ROOT/'runs'/study/'summary.json').read_text());assert len(rows)==240
  result=[]
  for city in ['los_angeles','luxembourg','pedralbes']:
   for policy in ['content','deadline']:
    blocks=[]
    for seed in range(4201,4221):
     block={r['policy']:r for r in rows if r['city']==city and r['seed']==seed};assert set(block)=={'none','rules','content','deadline'};blocks.append(block)
    contrasts={}
    for metric in ['co2_kg','arrived']:
     d=[float(b[policy][metric])-float(b['rules'][metric]) for b in blocks];rng=random.Random(8141);boot=sorted(statistics.mean(rng.choices(d,k=20)) for _ in range(10000))
     contrasts[metric]={'mean':statistics.mean(d),'bootstrap_95':[boot[249],boot[9749]]}
    result.append({'city':city,'policy_minus_template':policy,'n_pairs':20,'contrasts':contrasts})
  output[study]=result
 target=ROOT/'outputs';target.mkdir(exist_ok=True);(target/'reproduced_city_contrasts.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
