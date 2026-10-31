"""Development-only alignment, declared before cohort counts; no outcome reads."""
import fcntl,hashlib,json,xml.etree.ElementTree as E
from pathlib import Path
import pandas as pd
from v2x.credentials import ROOT
O=ROOT/'runs/alignment_v1'
PLAN=dict(stage='development_alignment_not_confirmatory',cities=['los_angeles','luxembourg','pedralbes'],seed=4101,trace_profiles=[1,6],trace_epoch_s=300,trace_offset_window_s=[0,90],advisory_departure_window_s=[310,370],interval_convention='Left closed, right open for TX and scheduled departure',observation_period_s=5,max_age_s=5,simulation_horizon_s=2400,closure_s=[300,900],compliance=[.25,.5,1],routing='Existing fixed route alternatives and nested draws; no replacement of demand',eligibility='Scheduled departure in window, originally exposed, existing lane-preflighted alternative. Include eligible noncompliers, missed insertion/decision points, transport/audit failures in denominator.',rationale='Fixed 300s background warm-up,10s receiver startup,60s cohort window,20s remaining TX support. No selecting windows from emissions, realized arrivals, packet delivery or auditor outcomes.',not_frozen=['held-out samples','new message/incident families','model revisions','deadline calibration','statistical analysis','mobile-trace validation'],paid_budget_changes=False)
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Complete')
  plan=O/'plan.json'
  if plan.exists():assert json.loads(plan.read_text())==PLAN
  else:plan.write_text(json.dumps(PLAN,indent=2))
  inputs={};rows=[]
  for city in PLAN['cities']:
   fxp=ROOT/'runs/city_uptake_v3'/city/'fixture.json';rp=ROOT/'runs/city_preflight_v1'/city/'accepted.xml'
   for p in [fxp,rp]:inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
   fx=json.loads(fxp.read_text());vehicles=E.parse(rp).getroot().findall('vehicle');cohort=[];window=[];exposed=[]
   for v in vehicles:
    ident=v.get('id');depart=float(v.get('depart'))
    if 310<=depart<370:
     window.append(ident)
     if fx['edge'] in v.find('route').get('edges').split():exposed.append(ident)
     if ident in fx['eligible_alternatives']:cohort.append(dict(id=ident,scheduled_departure_s=depart,compliance_draw=fx['draws'][ident]))
   row=dict(city=city,requested=600,accepted=len(vehicles),excluded=600-len(vehicles),departures_in_window=len(window),exposed_in_window=len(exposed),eligible=len(cohort),assigned={str(q):sum(r['compliance_draw']<q for r in cohort) for q in PLAN['compliance']},cohort=cohort)
   rows.append(row)
  traces=[]
  for profile in PLAN['trace_profiles']:
   p=ROOT/f'data/derived/see_parkinglot_{profile}.csv';inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();d=pd.read_csv(p);assert d.tx_offset_s.max()>=90
   traces.append(dict(profile=profile,native_span_s=float(d.tx_offset_s.max()),tx_in_fixed_window=int(((d.tx_offset_s>=0)&(d.tx_offset_s<90)).sum())))
  (O/'inputs.json').write_text(json.dumps(inputs,indent=2));(O/'summary.json').write_text(json.dumps(dict(cities=rows,traces=traces),indent=2));print(json.dumps(dict(cities=rows,traces=traces),indent=2))
  manifest=dict(plan_sha256=hashlib.sha256(plan.read_bytes()).hexdigest(),inputs=inputs,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),status='Development construction freeze only; no confirmatory or effectiveness claim')
  (O/'manifest.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
