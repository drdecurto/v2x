"""Map-derived DTLA development scenario; synthetic demand, inferred signal plans."""
import json,subprocess,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import sumolib,sumo
from v2x.credentials import ROOT
D=ROOT/'data/derived/los_angeles';tools=Path(sumo.__file__).parent/'tools';out=ROOT/'runs/la_development_v1';out.mkdir(exist_ok=True)
net=sumolib.net.readNet(str(D/'downtown.net.xml'))
for label,period in [('moderate',1.5),('busy',.75)]:
 p=out/label;p.mkdir(exist_ok=True)
 if not (p/'routes.rou.xml').exists():
  command=[str(ROOT/'.venv/bin/python'),str(tools/'randomTrips.py'),'-n',str(D/'downtown.net.xml'),'-o',str(p/'trips.trips.xml'),'-r',str(p/'routes.rou.xml'),'--seed','4101','--begin','0','--end','900','--period',str(period),'--min-distance','600','--max-distance','2500','--fringe-factor','5','--vehicle-class','passenger','--prefix',label,'--trip-attributes','departLane="best" departSpeed="max"','--validate']
  with (p/'routing.log').open('w') as f:subprocess.run(command,check=True,stdout=f,stderr=f)
 cfg=f'''<configuration><input><net-file value="../../../data/derived/los_angeles/downtown.net.xml"/><route-files value="routes.rou.xml"/><additional-files value="../../../data/derived/los_angeles/buildings.poly.xml"/></input><time><begin value="0"/><end value="2400"/><step-length value="0.5"/></time><processing><time-to-teleport value="-1"/></processing><random_number><seed value="4101"/></random_number><output><tripinfo-output value="tripinfo.xml"/><tripinfo-output.write-unfinished value="true"/><summary-output value="summary.xml"/><statistic-output value="statistics.xml"/></output><report><no-step-log value="true"/><duration-log.disable value="true"/><error-log value="simulation_errors.log"/></report></configuration>'''
 (p/'scenario.sumocfg').write_text(cfg)
 if not (p/'statistics.xml').exists():
  with (p/'run.log').open('w') as f:subprocess.run([str(ROOT/'.venv/bin/sumo'),'-c',str(p/'scenario.sumocfg')],check=True,stdout=f,stderr=f)
report={'place':'Downtown Los Angeles','source_manifest':'data/raw/los_angeles/source.json','edges':len(net.getEdges()),'junctions':len(net.getNodes()),'signal_controllers':len(net.getTrafficLights()),'lanes':sum(len(e.getLanes()) for e in net.getEdges()),'polygons':len(ET.parse(D/'buildings.poly.xml').getroot().findall('poly')),'net_sha256':hashlib.sha256((D/'downtown.net.xml').read_bytes()).hexdigest(),'demand_note':'Synthetic random origin-destination development traffic; not observed Los Angeles traffic counts. Import infers missing lanes/connections/speeds and actuated signal plans.','scenarios':[]}
for label in ['moderate','busy']:
 p=out/label;routes=ET.parse(p/'routes.rou.xml').getroot();trips=ET.parse(p/'tripinfo.xml').getroot();summary=ET.parse(p/'summary.xml').getroot();stats=ET.parse(p/'statistics.xml').getroot()
 finished=[t for t in trips if float(t.get('arrival','-1'))>=0];unfinished=[t for t in trips if float(t.get('arrival','-1'))<0]
 report['scenarios'].append({'name':label,'seed':4101,'requested_trips':600 if label=='moderate' else 1200,'valid_routes':len(routes.findall('vehicle')),'arrived':len(finished),'unfinished_inserted':len(unfinished),'max_running':max(int(t.get('running')) for t in summary),'last_summary':summary[-1].attrib,'statistics':{x.tag:x.attrib for x in stats},'mean_completed_duration_s':sum(float(t.get('duration')) for t in finished)/len(finished)})
(ROOT/'reports/la_development.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
