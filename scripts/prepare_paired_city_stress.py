"""Freeze a matched traffic sensitivity; reuse exactly matching completed full-uptake blocks."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from v2x.credentials import ROOT
out=ROOT/'runs/paired_city_stress_v1';out.mkdir(exist_ok=True)
assert not (out/'plan.json').exists()
plan=dict(created_at=datetime.now(timezone.utc).isoformat(),stage='exploratory_matched_city_sensitivity_not_auditor_effect',seeds=list(range(4201,4221)),cities=['los_angeles','luxembourg','pedralbes'],arms=['no_diversion','full_diversion'],closure_s=[0,900],end_s=2400,primary=['arrived','running','pending','co2_kg'],analysis='Paired full-minus-none block differences, per-city 20-block bootstrap 95% intervals, seed 8141, 10000 resamples. Report CO2 jointly with completion; retain all exclusions, unfinished trips, safety and teleports. No radio or inference. Cases already used in development; not confirmatory.',reuse='Reuse the 12 completed preexisting_closure_v1 full-uptake blocks after input/output hashes; do not rerun duplicates.',purpose='Quantify whether incident routing has reproducible application consequences and whether unresolved simulator failures vary by intervention. This bounds traffic claims; it cannot demonstrate content-auditor benefit.')
(out/'plan.json').write_text(json.dumps(plan,indent=2))
source=(ROOT/'scripts/validate_preexisting_closure.py').read_text()
for arm in plan['arms']:
 target=out/arm;target.mkdir()
 s=source.replace("O=ROOT/'runs/preexisting_closure_v1'",f"O=ROOT/'runs/paired_city_stress_v1/{arm}'").replace('list(range(4201,4205))','list(range(4201,4221))').replace("uptake=1,","uptake="+('0' if arm=='no_diversion' else '1')+",").replace("First four previously constructed seeds per city, fixed before these outcomes; closure before departure, not a repair of mid-run cases","All twenty existing development seeds; frozen paired sensitivity, not a simulator repair")
 if arm=='no_diversion':s=s.replace("try:c.vehicle.setRoute(ident,cohort[ident]['route']);d['applied']=True","try:d['error']='assigned_no_diversion'")
 script=ROOT/'scripts'/f'run_paired_city_{arm}.py';script.write_text(s)
 if arm=='full_diversion':
  for city in plan['cities']:
   for seed in range(4201,4205):
    old=ROOT/'runs/preexisting_closure_v1'/city/str(seed);dest=target/city/str(seed)
    assert json.loads((old/'result.json').read_text())['accounting_valid']
    shutil.copytree(old,dest)
    (dest/'reused_from.json').write_text(json.dumps(dict(source=str(old.relative_to(ROOT)),hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in old.iterdir() if p.is_file()}),indent=2))
(out/'freeze.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'plan.json',ROOT/'scripts/run_paired_city_no_diversion.py',ROOT/'scripts/run_paired_city_full_diversion.py']},indent=2))
