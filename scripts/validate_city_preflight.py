"""Common prospective import/preflight rule; no inference or outcome filtering."""
import fcntl,hashlib,json,subprocess,xml.etree.ElementTree as E
from v2x.credentials import ROOT
from audit_route_lanes import audit
O=ROOT/'runs/city_preflight_v1';B=ROOT/'.venv/bin'
PLAN={'cities':['los_angeles','luxembourg','pedralbes'],'seed':4101,'requested_per_city':600,'demand':'Reuse original stored OD requests, no replenishment','import':'Same original OSM; no guessed ramps; OSM lane access; otherwise original geometry/junction/TLS/passenger/turn-lane options','preflight':'Reject unroutable requests and legal passenger lane-reachability failures before outcomes; unlimited lane-change distance is a necessary, not sufficient, check','horizon_s':2400,'step_s':.5,'teleport':False,'scope':'Development construction validation, no calibrated city traffic or policy comparison'}
def save(p,x):p.write_text(json.dumps(x,indent=2))
def run(args,p):
 with p.open('w') as f:subprocess.run(list(map(str,args)),stdout=f,stderr=f,check=True)
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Completed')
  if (O/'plan.json').exists():assert json.loads((O/'plan.json').read_text())==PLAN
  else:save(O/'plan.json',PLAN)
  rows=[]
  for city in PLAN['cities']:
   p=O/city;p.mkdir(exist_ok=True);net=p/'city.net.xml'
   osm=ROOT/'data/raw'/city/('downtown.osm.xml' if city=='los_angeles' else 'city.osm.xml')
   trips=ROOT/'runs/city_infrastructure_v2'/city/'trips.xml'
   if not net.exists():
    args=[B/'netconvert','--osm-files',osm,'--output-file',net,'--geometry.remove','--ramps.guess','false','--osm.lane-access','true','--junctions.join','--tls.guess-signals','--tls.discard-simple','--tls.join','--tls.default-type','actuated','--keep-edges.by-vclass','passenger','--remove-edges.isolated','--osm.turn-lanes','--output.street-names']
    save(p/'import_command.json',list(map(str,args)));run(args,p/'import.log')
   save(p/'inputs.json',{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [osm,trips,net]})
   if not (p/'routed.xml').exists():run([B/'duarouter','-n',net,'-r',trips,'-o',p/'routed.xml','--seed',4101,'--ignore-errors','true','--no-step-log'],p/'routing.log')
   tree=E.parse(p/'routed.xml');vehicles=tree.getroot().findall('vehicle');requested={v.get('id') for v in E.parse(trips).getroot().findall('trip')};routed={v.get('id') for v in vehicles}
   report=audit(net,p/'routed.xml');bad={v['vehicle'] for v in report['failures']};accepted=routed-bad
   save(p/'preflight.json',{'requested_ids':sorted(requested),'unroutable':sorted(requested-routed),'lane_failures':report['failures'],'accepted_ids':sorted(accepted)})
   for v in vehicles:
    if v.get('id') in bad:tree.getroot().remove(v)
   tree.write(p/'accepted.xml',encoding='utf-8',xml_declaration=True)
   if not (p/'statistics.xml').exists():run([B/'sumo','-n',net,'-r',p/'accepted.xml','--seed',4101,'--end',2400,'--step-length',.5,'--time-to-teleport',-1,'--tripinfo-output',p/'tripinfo.xml','--tripinfo-output.write-unfinished','true','--statistic-output',p/'statistics.xml','--error-log',p/'errors.log','--no-step-log'],p/'run.log')
   st=E.parse(p/'statistics.xml').getroot();ti=E.parse(p/'tripinfo.xml').getroot();v=st.find('vehicles');arrived=sum(float(x.get('arrival',-1))>=0 for x in ti)
   row=dict(city=city,requested=len(requested),unroutable=len(requested-routed),lane_rejected=len(bad),accepted=len(accepted),arrived=arrived,running=int(v.get('running')),pending=int(v.get('waiting')),safety=st.find('safety').attrib,teleports=st.find('teleports').attrib)
   assert row['requested']==600==row['unroutable']+row['lane_rejected']+row['arrived']+row['running']+row['pending']
   save(p/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
