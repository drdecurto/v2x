"""Finite development contract check, no traffic execution or model calls."""
import fcntl, hashlib, json, xml.etree.ElementTree as E
from pathlib import Path
from v2x.credentials import ROOT
from v2x.city_consumer import consume_city
from v2x.evidence import EvidenceReceiver
O=ROOT/'runs/city_consumer_v1'

def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Already complete')
  cases=['supported','unsupported_green','contradicted','qualified','stale','changed_version','missed_decision']
  plan=dict(stage='development_contract_only',cases=cases,cities=['los_angeles','luxembourg','pedralbes'],policies=['none','rules','content','deadline'],verdicts='Scripted accept except unsupported_green reject; not model observations',transport='Direct receiver injection, no empirical packet timing',traffic='Routes selected only, no SUMO execution or new CO2 results')
  (O/'plan.json').write_text(json.dumps(plan,indent=2));rows=[];sources={}
  for city in plan['cities']:
   path=ROOT/'runs/city_uptake_v3'/city/'fixture.json';fx=json.loads(path.read_text());sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
   ident=sorted(fx['eligible_alternatives'])[0];alt=fx['eligible_alternatives'][ident]
   routefile=ROOT/'runs/city_preflight_v1'/city/'accepted.xml';sources[str(routefile.relative_to(ROOT))]=hashlib.sha256(routefile.read_bytes()).hexdigest()
   original=next(v.find('route').get('edges').split() for v in E.parse(routefile).getroot().findall('vehicle') if v.get('id')==ident)
   assert fx['edge'] in original and fx['edge'] not in alt
   for case in cases:
    for policy in plan['policies']:
     e=dict(source_id=city,sequence=1,observed_at_s=0,road_A_closed=True,road_B_available=True);r=EvidenceReceiver(5);r.receive(e,0)
     now=6 if case=='stale' else 1
     if case=='changed_version':r.receive(dict(e,sequence=2,observed_at_s=1),1)
     text={'supported':'The observed road is closed. Consider the available alternative.','unsupported_green':'The alternative guarantees a 40% CO2 reduction.','contradicted':'The observed road is open. Continue on it.','qualified':'The alternative may help; its emissions outcome is unknown.'}.get(case,'The observed road is closed. Consider the available alternative.')
     a=dict(issued_s=0,expires_s=20,road='A',action='main' if case=='contradicted' else 'detour',claimed_closed=case!='contradicted',text=text)
     result=consume_city(policy,a,r,now,vehicle_id=ident,original_route=original,alternative_route=alt,before_decision=case!='missed_decision',compliant=True,audited=e,verdict='reject' if case=='unsupported_green' else 'accept',deadline_fallback=True)
     rows.append(dict(city=city,case=case,policy=policy,now=now,advisory=a,audited=e,result=result))
  (O/'decisions.json').write_text(json.dumps(rows,indent=2));(O/'source_hashes.json').write_text(json.dumps(sources,indent=2))
  summary=dict(decisions=len(rows),selected=sum(x['result']['route_selected'] for x in rows),admitted=sum(x['result']['admit'] for x in rows),unsupported_free_text_admitted=sum(x['case']=='unsupported_green' and x['result']['text'] for x in rows),note=plan)
  (O/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
