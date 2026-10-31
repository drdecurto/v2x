"""Reproducible descriptive summaries; incomplete runs never become complete results."""
import hashlib,json,math,statistics,random,xml.etree.ElementTree as E
from decimal import Decimal
from pathlib import Path
from v2x.credentials import ROOT

def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def wilson(k,n):
 if not n:return None
 z=1.95996398454;a=k/n;d=1+z*z/n;c=(a+z*z/(2*n))/d;h=z*math.sqrt(a*(1-a)/n+z*z/(4*n*n))/d
 return [c-h,c+h]
def main():
 o=ROOT/'runs/advisory_benchmark_v1';cases={x['id']:x for x in json.loads((o/'cases.json').read_text())};freeze=json.loads((o/'freeze.json').read_text())
 for name in ['cases','plan']:assert hashlib.sha256((o/(name+'.json')).read_bytes()).hexdigest()==freeze[name+'_sha256']
 summaries=[];models={}
 for p in sorted(o.glob('*.jsonl')):
  rows=[json.loads(x) for x in p.read_text().splitlines()];assert len({r['id'] for r in rows})==len(rows);assert all(r['id'] in cases for r in rows)
  models[rows[0]['model']]={r['id']:r for r in rows}
  for cat in sorted({c['category'] for c in cases.values()}):
   subset=[r for r in rows if cases[r['id']]['category']==cat];n=len(subset);correct=sum(r.get('decision')==cases[r['id']]['expected'] for r in subset)
   summaries.append(dict(model=rows[0]['model'],category=cat,n=n,planned_n=30,correct=correct,failures=sum(r['status']!='ok' for r in subset),decisions={v:sum(r.get('decision')==v for r in subset) for v in ['accept','reject','unsure']},descriptive_wilson=wilson(correct,n),median_elapsed_s=statistics.median(r['elapsed_s'] for r in subset) if n else None))
 pairs=[]
 for i,a in enumerate(models):
  for b in list(models)[i+1:]:
   common=set(models[a])&set(models[b]);pairs.append(dict(a=a,b=b,n=len(common),disagreements=sum(models[a][k].get('decision')!=models[b][k].get('decision') for k in common)))
 dump(o/'analysis.json',dict(complete=len(models)==4 and all(len(v)==180 for v in models.values()),counts={m:len(v) for m,v in models.items()},categories=summaries,paired_disagreement=pairs,warning='Constructed template-dependent cases. Wilson intervals are descriptive only, not independent population inference. Revised rubric differs from earlier studies. Failures retained.'))
 o=ROOT/'runs/paired_city_stress_v1';plan=json.loads((o/'plan.json').read_text());rows=[];verified=0
 for city in plan['cities']:
  pairs=[]
  for seed in plan['seeds']:
   arms={}
   for arm in plan['arms']:
    p=o/arm/city/str(seed)
    if not (p/'result.json').exists():continue
    r=json.loads((p/'result.json').read_text());trips=E.parse(p/'tripinfo.xml').getroot().findall('tripinfo');st=E.parse(p/'statistics.xml').getroot()
    assert r['arrived']==sum(float(t.get('arrival'))>=0 for t in trips)
    assert r['co2_kg']==str(sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/Decimal(1000000))
    assert r['running']==int(st.find('vehicles').get('running'))
    assert r['arrived']+r['running']+r['pending']+r['excluded']==600
    verified+=1;arms[arm]=r
   if len(arms)==2:
    a,b=arms['no_diversion'],arms['full_diversion'];assert a['accepted']==b['accepted'] and a['eligible']==b['eligible'];pairs.append(dict(seed=seed,no_diversion=a,full_diversion=b))
  metrics={}
  for metric in ['co2_kg','arrived','running','pending']:
   differences=[float(p['full_diversion'][metric])-float(p['no_diversion'][metric]) for p in pairs]
   if differences:
    rng=random.Random(8141);n=len(differences);boot=sorted(sum(rng.choices(differences,k=n))/n for _ in range(10000))
    metrics[metric]=dict(mean_full_minus_none=statistics.mean(differences),bootstrap_95=[boot[249],boot[9749]],n_blocks=n)
  rows.append(dict(city=city,paired_blocks=len(pairs),planned_blocks=20,metrics=metrics,pairs=pairs))
 dump(o/'analysis.json',dict(complete=verified==120,independently_verified_blocks=verified,cities=rows,warning='Exploratory paired routing stress test. Existing development seeds, synthetic demand, unresolved city dynamics. No communication or LLM effect. Interpret emissions jointly with completion.'))
 print(json.dumps(dict(advisory=json.loads((ROOT/'runs/advisory_benchmark_v1/analysis.json').read_text())['counts'],city_verified_blocks=verified)))
if __name__=='__main__':main()
