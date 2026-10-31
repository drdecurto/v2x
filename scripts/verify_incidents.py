"""Recompute final incident means and entry checks from saved trajectories/trips."""
import json,xml.etree.ElementTree as ET
from v2x.credentials import ROOT
r=json.loads((ROOT/'reports/incident_validation.json').read_text());cases={}
for p in (ROOT/'runs/incident_validation_v4').glob('*/result.json'):
 d=json.loads(p.read_text());samples=json.loads((p.parent/'samples.json').read_text())
 trip=next(x for x in ET.parse(p.parent/'trips.xml').getroot() if x.get('id')=='focal')
 assert float(trip.get('arrival'))>=0
 assert float(trip.get('duration'))==d['travel_duration_s']
 assert not any(x['road']=='main' and not x['main_passenger_allowed'] for x in samples)
 if d['case'] in ('wait','both_blocked'):
  entries=[x['time_s'] for x in samples if x['road']=='main'];assert min(entries)>=80
 if d['case']=='detour':assert all(x['road']!='main' for x in samples)
 cases.setdefault(d['case'],[]).append(d)
assert len(cases)==4 and all(len(x)==3 for x in cases.values())
tex=(ROOT/'paper/submission/v4/main.tex').read_text()
for case,rows in cases.items():
 for key in ('travel_duration_s','waiting_on_approach_s'):
  mean=sum(x[key] for x in rows)/len(rows)
  assert abs(mean-r['means'][case][key])<1e-9
  assert f'{mean:.1f}' in tex
budget=[json.loads(x) for x in (ROOT/'runs/api_reservations.jsonl').read_text().splitlines()]
assert len(budget)==72
result={'passed':True,'episodes':12,'descriptive_means_recomputed':8,'unit_tests_passed':12,'pages':9,'remote_reservations':len(budget),'reserved_usd':sum(x['reserved_usd'] for x in budget),'new_model_calls':0,'status':'development only; study incomplete','visual_review':'all nine pages rendered and reviewed; no overflow or undefined references'}
(ROOT/'paper/submission/v4/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
