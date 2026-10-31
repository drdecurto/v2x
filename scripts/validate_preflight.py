"""Development validation of preflight filtering; all exclusions remain accounted for."""
import json,subprocess,xml.etree.ElementTree as E,fcntl,hashlib,shutil
from pathlib import Path
import sumo
from audit_route_lanes import audit
from v2x.credentials import ROOT
O=ROOT/'runs/preflight_validation_v1';O.mkdir(exist_ok=True)
B=ROOT/'.venv/bin';N=ROOT/'runs/pedralbes_lane_access_v1/no_guessed_ramps_lane_access/city.net.xml'
plan={'seeds':[4101,4102,4103],'purpose':'development, not held-out confirmation','requested_per_seed':600,'network_sha256':hashlib.sha256(N.read_bytes()).hexdigest(),'demand_domain':'original Pedralbes network; period1.5, depart0-900,min600m,max2500m,fringe5','rules':'duarouter unreachable and necessary lane-feasibility failures rejected before traffic outcomes; no replenishment; no outcome exclusions','end_s':2400,'step_s':.5,'teleport':False,'arms':['unfiltered','preflight'],'caveat':'Filtering changes traffic load; completion differences are not a causal policy benefit.'}
if not (O/'plan.json').exists():(O/'plan.json').write_text(json.dumps(plan,indent=2))
def run(args,log):
 with log.open('w') as f:subprocess.run(list(map(str,args)),stdout=f,stderr=f,check=True)
with (O/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 rows=[]
 for seed in plan['seeds']:
  p=O/str(seed);p.mkdir(exist_ok=True)
  if not (p/'trips.xml').exists():
   if seed==4101:shutil.copy2(ROOT/'runs/city_infrastructure_v2/pedralbes/trips.xml',p/'trips.xml')
   else:run([B/'python',Path(sumo.__file__).parent/'tools/randomTrips.py','-n',ROOT/'data/derived/pedralbes/city.net.xml','-o',p/'trips.xml','--seed',seed,'--begin',0,'--end',900,'--period',1.5,'--min-distance',600,'--max-distance',2500,'--fringe-factor',5,'--vehicle-class','passenger','--trip-attributes','departLane="best" departSpeed="max"'],p/'demand.log')
  if not (p/'routed.xml').exists():run([B/'duarouter','-n',N,'-r',p/'trips.xml','-o',p/'routed.xml','--seed',seed,'--ignore-errors','true','--no-step-log'],p/'routing.log')
  requests={v.get('id') for v in E.parse(p/'trips.xml').getroot().findall('trip')};tree=E.parse(p/'routed.xml');vehicles=tree.getroot().findall('vehicle');routed={v.get('id') for v in vehicles};report=audit(N,p/'routed.xml');bad={v['vehicle'] for v in report['failures']}
  rejection={'unroutable':sorted(requests-routed),'lane_infeasible':report['failures'],'accepted_ids':sorted(routed-bad)};(p/'preflight.json').write_text(json.dumps(rejection,indent=2))
  for v in vehicles:
   if v.get('id') in bad:tree.getroot().remove(v)
  tree.write(p/'accepted.xml',encoding='utf-8',xml_declaration=True)
  for arm in plan['arms']:
   d=p/arm;d.mkdir(exist_ok=True)
   if not (d/'statistics.xml').exists():
    if seed==4101 and arm=='unfiltered':
     src=ROOT/'runs/pedralbes_lane_access_v1/no_guessed_ramps_lane_access'
     for file in ['statistics.xml','tripinfo.xml','errors.log']:shutil.copy2(src/file,d/file)
    else:run([B/'sumo','-n',N,'-r',p/('accepted.xml' if arm=='preflight' else 'routed.xml'),'--seed',seed,'--end',2400,'--step-length',.5,'--time-to-teleport',-1,'--tripinfo-output',d/'tripinfo.xml','--tripinfo-output.write-unfinished','true','--statistic-output',d/'statistics.xml','--error-log',d/'errors.log','--no-step-log'],d/'run.log')
   st=E.parse(d/'statistics.xml').getroot();tr=E.parse(d/'tripinfo.xml').getroot();v=st.find('vehicles');a=sum(float(x.get('arrival',-1))>=0 for x in tr);excluded=len(requests-routed)+(len(bad) if arm=='preflight' else 0)
   row={'seed':seed,'arm':arm,'requested':len(requests),'unroutable':len(requests-routed),'lane_rejected':len(bad) if arm=='preflight' else 0,'arrived':a,'running':int(v.get('running')),'pending':int(v.get('waiting')),'safety':st.find('safety').attrib,'teleports':st.find('teleports').attrib}
   assert a+row['running']+row['pending']+excluded==len(requests)==600
   rows.append(row);print(row,flush=True)
 (O/'summary.json').write_text(json.dumps(rows,indent=2))
