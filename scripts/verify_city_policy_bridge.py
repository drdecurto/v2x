"""Independent accounting, timing, packet and paired-input validation with partial reporting."""
import hashlib,json,math,random,statistics,xml.etree.ElementTree as E
from decimal import Decimal
from collections import Counter
from pathlib import Path
import pandas as pd
from v2x.credentials import ROOT
O=ROOT/'runs/city_policy_bridge_v1'
def main():
 inputs=json.loads((O/'inputs.json').read_text())
 for name,h in inputs.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 cases={r['id']:r for r in json.loads((O/'cases.json').read_text())};assignment=json.loads((O/'assignments.json').read_text())
 audits={r['id']:r for r in map(json.loads,(O/'audits.jsonl').read_text().splitlines())};packets=pd.read_csv(ROOT/'data/derived/see_parkinglot_6.csv').to_dict('records');all_rows=[];verified_decisions=0;pairhash={}
 for file in sorted(O.glob('*/*/*/result.json')):
  p=file.parent;r=json.loads(file.read_text());city,seed,policy=r['city'],r['seed'],r['policy'];key=(city,seed)
  digest=hashlib.sha256((p/'routes.xml').read_bytes()).hexdigest()
  if key in pairhash:assert digest==pairhash[key]
  pairhash[key]=digest
  trips=E.parse(p/'tripinfo.xml').getroot().findall('tripinfo');st=E.parse(p/'statistics.xml').getroot()
  assert r['arrived']==sum(float(t.get('arrival'))>=0 for t in trips)
  for k,xmlkey in [('running','running'),('pending','waiting')]:assert r[k]==int(st.find('vehicles').get(xmlkey))
  assert sum(r[k] for k in ['arrived','running','pending','excluded'])==600
  assert Decimal(r['co2_kg'])==sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/Decimal(1000000)
  obs=json.loads((p/'observations.json').read_text());deliveries=json.loads((p/'deliveries.json').read_text());decisions=json.loads((p/'decisions.json').read_text())
  assert len(obs)==481
  for i,ob in enumerate(obs):assert ob['sequence']==i and ob['observed_at_s']==i*5 and ob['road_A_closed']==(i*5<900)
  assert len(deliveries)==sum(bool(q['received']) for q in packets)
  for d in deliveries:
   packet=packets[d['index']];tx=300+float(packet['tx_offset_s']);expected=tx+float(packet['delay_s'])
   assert bool(packet['received']) and abs(d['rx_s']-expected)<1e-8
   assert d['rx_s']<=d['processed_s']<d['rx_s']+.50000001
   assert d['evidence']==obs[int(tx//5)]
  fx=json.loads((ROOT/f'runs/replication_incidents_v1/{city}/{seed}/result.json').read_text());cohort={v['id']:v for v in fx['cohort']}
  assert len({d['vehicle_id'] for d in decisions})==len(decisions)
  for d in decisions:
   ident=d['vehicle_id'];assert d['case_id']==assignment[f'{city}/{seed}/{ident}'];case=cases[d['case_id']];rec=audits[d['case_id']]
   assert d['expected']==case['expected'] and d['category']==case['category']
   delay=0 if policy in ['none','rules'] or d['audited'] is None else min(rec['elapsed_s'],5 if policy=='content' else 2)
   assert abs(d['scheduled_s']-d['request_s']-delay)<1e-8
   assert d['scheduled_s']<=d['consumed_s']<d['scheduled_s']+.50000001
   # Reconstruct current and requested evidence from the delivered records, without using receiver code.
   def evidence_at(now):
    known=None
    for entry in deliveries:
     if entry['processed_s']>now:break
     if entry['status']=='updated':known=entry['evidence']
    return known if known and now-known['observed_at_s']<=5 else None
   assert d['audited']==evidence_at(d['request_s']);assert d['current']==evidence_at(d['consumed_s'])
   current=d['current'];now=d['consumed_s'];audited=d['audited'];fallback=policy=='deadline' and (rec['elapsed_s']>=2 or rec['status']!='ok')
   if now>=d['request_s']+5:mode='invalid_or_expired'
   elif not d['before_decision']:mode='decision_point_passed'
   elif current is None:mode='evidence_unavailable'
   elif not current['road_B_available']:mode='observed_route_unavailable'
   elif policy=='none':mode='unchecked'
   elif not current['road_A_closed']:mode='rules_reject'
   elif policy=='rules' or fallback:mode='verified_template'
   elif audited is None:mode='audit_missing'
   elif audited['source_id']!=current['source_id'] or audited['sequence']!=current['sequence']:mode='audit_version_changed'
   elif not 0<=now-audited['observed_at_s']<=5:mode='audit_evidence_age'
   else:
    verdict=rec.get('decision') if rec['status']=='ok' and (policy!='content' or rec['elapsed_s']<5) else None
    mode='content_accept' if verdict=='accept' else 'content_'+str(verdict)
   assert d['result']['mode']==mode,(p,d,mode)
   assert d['result']['admit']==(mode in ['unchecked','verified_template','content_accept'])
   assert d['result']['text']==(mode in ['unchecked','content_accept'])
   if d['applied']:assert d['route_after']==cohort[ident]['route'] and d['result']['route_selected'] and d['error'] is None
  for k,expected in [('decisions',len(decisions)),('applied',sum(d['applied'] for d in decisions)),('harmful_original_text',sum(d['expected']=='reject' and d['result']['text'] for d in decisions)),('clean_admitted',sum(d['expected']=='accept' and d['result']['admit'] for d in decisions))]:assert r[k]==expected
  r=dict(r,modes=dict(Counter(d['result']['mode'] for d in decisions)));all_rows.append(r);verified_decisions+=len(decisions)
 summary=[]
 for city in ['los_angeles','luxembourg','pedralbes']:
  for policy in ['none','rules','content','deadline']:
   rows=[r for r in all_rows if r['city']==city and r['policy']==policy];baseline={r['seed']:r for r in all_rows if r['city']==city and r['policy']=='rules'};metrics={}
   for key in ['co2_kg','arrived','applied','harmful_original_text','clean_admitted']:
    values=[float(r[key])-float(baseline[r['seed']][key]) for r in rows if r['seed'] in baseline]
    if values:
     rng=random.Random(8141);n=len(values);boot=sorted(sum(rng.choices(values,k=n))/n for _ in range(10000));metrics[key]=dict(n_pairs=n,mean_policy_minus_rules=statistics.mean(values),bootstrap_95=[boot[249],boot[9749]])
   summary.append(dict(city=city,policy=policy,completed_blocks=len(rows),totals={k:sum(float(r[k]) for r in rows) for k in ['accepted','excluded','arrived','running','pending','co2_kg','decisions','applied','clean','clean_admitted','harmful_original_text','uncertain_original_text']},paired_vs_rules=metrics,modes=dict(sum((Counter(r['modes']) for r in rows),Counter()))))
 result=dict(complete=len(all_rows)==240,verified_blocks=len(all_rows),verified_decisions=verified_decisions,source_hashes=len(inputs),summary=summary)
 (O/'verification_and_analysis.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='summary'}))
if __name__=='__main__':main()
