"""Predeclared import sensitivity, identical OD requests; no post-hoc exclusions."""
import json,subprocess,xml.etree.ElementTree as E,fcntl
from pathlib import Path
from v2x.credentials import ROOT
out=ROOT/'runs/pedralbes_lane_access_v1';out.mkdir(exist_ok=True)
plan={'status':'development diagnosis only','variants':{'no_guessed_ramps_lane_access':['--ramps.guess','false','--osm.lane-access','true']},'fixed':'original OSM, OD requests, departure times, seed 4101, horizon 2400, step .5, teleport disabled','accounting':'retain unroutable requests; route changes prevent interpreting contrasts as placement/auditor effects'}
if not (out/'plan.json').exists():(out/'plan.json').write_text(json.dumps(plan,indent=2))
def run(args,log):
 with log.open('w') as f:return subprocess.run(list(map(str,args)),stdout=f,stderr=f).returncode
with (out/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 results=[]
 for name,opts in plan['variants'].items():
  p=out/name;p.mkdir(exist_ok=True)
  if (p/'result.json').exists():results.append(json.loads((p/'result.json').read_text()));continue
  command=json.loads((ROOT/'data/derived/pedralbes/import_command.json').read_text());command[command.index('--output-file')+1]=str(p/'city.net.xml');command.remove('--ramps.guess');command+=opts
  assert run(command,p/'import.log')==0
  trips=ROOT/'runs/city_infrastructure_v2/pedralbes/trips.xml'
  routecode=run([ROOT/'.venv/bin/duarouter','-n',p/'city.net.xml','-r',trips,'-o',p/'routes.rou.xml','--seed','4101','--ignore-errors','true','--no-step-log'],p/'routing.log')
  assert routecode==0
  routed=len(E.parse(p/'routes.rou.xml').getroot().findall('vehicle'));requested=len(E.parse(trips).getroot().findall('trip'))
  assert run([ROOT/'.venv/bin/sumo','-n',p/'city.net.xml','-r',p/'routes.rou.xml','--seed','4101','--step-length','.5','--end','2400','--time-to-teleport','-1','--tripinfo-output',p/'tripinfo.xml','--tripinfo-output.write-unfinished','true','--statistic-output',p/'statistics.xml','--no-step-log','--error-log',p/'errors.log'],p/'simulation.log')==0
  stats=E.parse(p/'statistics.xml').getroot();v=stats.find('vehicles');tr=E.parse(p/'tripinfo.xml').getroot();arrived=sum(float(t.get('arrival',-1))>=0 for t in tr)
  result={'variant':name,'requested':requested,'routed':routed,'unroutable':requested-routed,'arrived':arrived,'running':int(v.get('running')),'waiting':int(v.get('waiting')),'collisions':int(stats.find('safety').get('collisions')),'teleports':int(stats.find('teleports').get('total'))}
  assert arrived+result['running']+result['waiting']+result['unroutable']==requested
  (p/'result.json').write_text(json.dumps(result,indent=2));results.append(result);print(result,flush=True)
 (out/'summary.json').write_text(json.dumps(results,indent=2))
