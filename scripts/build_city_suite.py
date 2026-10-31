"""Reproducible map imports and instrumented development smoke tests, not calibrated traffic."""
import json, hashlib, subprocess, urllib.request, urllib.error, datetime, shutil, xml.etree.ElementTree as ET
from pathlib import Path
import sumo, sumolib, traci
from v2x.credentials import ROOT
CITIES={'los_angeles':None,'luxembourg':[6.118,49.594,6.145,49.618],'pedralbes':[2.099,41.382,2.127,41.404]}
B=ROOT/'.venv/bin'; S=Path(sumo.__file__).parent

def run(args,log):
 with log.open('w') as f: subprocess.run([str(x) for x in args],stdout=f,stderr=f,check=True)
def build(city,bbox):
 d=ROOT/'data/derived'/city; d.mkdir(parents=True,exist_ok=True)
 raw=ROOT/'data/raw'/city;raw.mkdir(parents=True,exist_ok=True)
 netpath=d/('downtown.net.xml' if city=='los_angeles' else 'city.net.xml')
 if bbox:
  osm=raw/'city.osm.xml';url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,bbox))
  if not osm.exists():
   # Small tiled requests avoid the OSM API node-count limit. Preserve exact source tiles.
   west,south,east,north=bbox; merged=ET.Element('osm',version='0.6',generator='V2X tiled import');seen=set();urls=[]
   for ix in range(3):
    for iy in range(3):
     tile=[west+(east-west)*ix/3,south+(north-south)*iy/3,west+(east-west)*(ix+1)/3,south+(north-south)*(iy+1)/3]
     u='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(f'{x:.7f}' for x in tile);urls.append(u)
     tp=raw/f'tile_{ix}_{iy}.osm.xml'
     if not tp.exists():
      with urllib.request.urlopen(u,timeout=120) as r: chunk=r.read(20_000_001)
      if len(chunk)>20_000_000:raise ValueError('tile exceeds cap')
      ET.fromstring(chunk);tp.write_bytes(chunk)
     for element in ET.parse(tp).getroot():
      if element.tag not in ('node','way','relation'):continue
      key=(element.tag,element.get('id'))
      if key not in seen:seen.add(key);merged.append(element)
   merged[:]=sorted(merged,key=lambda x:({'node':0,'way':1,'relation':2}[x.tag],int(x.get('id'))))
   data=ET.tostring(merged,encoding='utf-8',xml_declaration=True);osm.write_bytes(data)
   (raw/'source.json').write_text(json.dumps({'url':url,'tile_urls':urls,'bbox':bbox,'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'attribution':'© OpenStreetMap contributors','license':'ODbL','license_url':'https://www.openstreetmap.org/copyright'},indent=2))
  if not netpath.exists():
   args=[B/'netconvert','--osm-files',osm,'--output-file',netpath,'--geometry.remove','--ramps.guess','--junctions.join','--tls.guess-signals','--tls.discard-simple','--tls.join','--tls.default-type','actuated','--keep-edges.by-vclass','passenger','--remove-edges.isolated','--osm.turn-lanes','--output.street-names']
   (d/'import_command.json').write_text(json.dumps(list(map(str,args)),indent=2));run(args,d/'import.log')
  if not (d/'buildings.poly.xml').exists():run([B/'polyconvert','--net-file',netpath,'--osm-files',osm,'--type-file',S/'data/typemap/osmPolyconvert.typ.xml','--output-file',d/'buildings.poly.xml'],d/'polygons.log')
  tree=ET.parse(d/'buildings.poly.xml')
  for p in tree.getroot():
   if p.tag not in ('poly','poi'):continue
   t=p.get('type','');p.set('color','175,210,225' if 'water' in t else '204,224,200' if any(x in t for x in ['park','forest','natural','leisure']) else '218,221,225' if 'building' in t else '237,238,240')
  tree.write(d/'publication.poly.xml',encoding='utf-8',xml_declaration=True)
  shutil.copy(ROOT/'data/derived/los_angeles/publication.view.xml',d/'publication.view.xml')
 n=sumolib.net.readNet(str(netpath));o=ROOT/'runs/city_infrastructure_v2'/city;o.mkdir(parents=True,exist_ok=True)
 if (o/'validation.json').exists():return json.loads((o/'validation.json').read_text())
 if not (o/'routes.rou.xml').exists():run([B/'python',S/'tools/randomTrips.py','-n',netpath,'-o',o/'trips.xml','-r',o/'routes.rou.xml','--seed','4101','--begin','0','--end','900','--period','1.5','--min-distance','600','--max-distance','2500','--fringe-factor','5','--vehicle-class','passenger','--trip-attributes','departLane="best" departSpeed="max"','--validate'],o/'routing.log')
 # Instrument the 12 busiest signal controllers according to the generated demand.
 counts={}
 for r in ET.parse(o/'routes.rou.xml').getroot().iter('route'):
  for e in r.get('edges','').split():counts[e]=counts.get(e,0)+1
 ranked=sorted(n.getTrafficLights(),key=lambda t:(-sum(counts.get(c[0].getEdge().getID(),0) for c in t.getConnections()),t.getID()))[:12]
 additional=ET.Element('additional');sensors=[];rsus=[]
 for k,t in enumerate(ranked):
  lanes={c[0].getID():c[0] for c in t.getConnections() if c[0].allows('passenger') and c[0].getLength()>10}
  if not lanes:continue
  xy=next(iter(lanes.values())).getEdge().getToNode().getCoord()
  ET.SubElement(additional,'poi',id=f'RSU_{k}',type='hypothetical_RSU',color='230,120,20',x=str(xy[0]),y=str(xy[1]),width='12',height='12',layer='100')
  rsus.append({'id':f'RSU_{k}','tls':t.getID(),'x':xy[0],'y':xy[1]})
  for j,(lid,lane) in enumerate(sorted(lanes.items())):
   length=min(80,lane.getLength()-2);ident=f'E2_{k}_{j}'
   ET.SubElement(additional,'laneAreaDetector',id=ident,lane=lid,pos=str(lane.getLength()-length-1),length=str(length),period='10',file=str(o/'detector_intervals.xml'),friendlyPos='true')
   sensors.append({'id':ident,'lane':lid,'tls':t.getID(),'length_m':length})
 ET.ElementTree(additional).write(o/'infrastructure.add.xml',encoding='utf-8',xml_declaration=True)
 (o/'infrastructure.json').write_text(json.dumps({'selection':'12 highest demand-weighted imported signal controllers; development placement only','sensors':sensors,'rsus':rsus},indent=2))
 cfg=f'<configuration><input><net-file value="{netpath}"/><route-files value="routes.rou.xml"/><additional-files value="{d / "publication.poly.xml"},infrastructure.add.xml"/></input><time><end value="2400"/><step-length value="0.5"/></time><processing><time-to-teleport value="-1"/></processing><random_number><seed value="4101"/></random_number><output><tripinfo-output value="tripinfo.xml"/><tripinfo-output.write-unfinished value="true"/><statistic-output value="statistics.xml"/></output><report><no-step-log value="true"/><error-log value="errors.log"/></report><gui_only><gui-settings-file value="{d / "publication.view.xml"}"/></gui_only></configuration>'
 (o/'scenario.sumocfg').write_text(cfg)
 traci.start([str(B/'sumo'),'-c',str(o/'scenario.sumocfg')],label=city,stdout=(o/'run.log').open('w'))
 c=traci.getConnection(city);peak=0;records=0;positive=0
 try:
  with (o/'observations.jsonl').open('w') as f:
   while c.simulation.getTime()<2400:
    c.simulationStep();tm=c.simulation.getTime();peak=max(peak,c.vehicle.getIDCount())
    if tm%5==0:
     for r in rsus:
      det=[s for s in sensors if s['tls']==r['tls']]
      obs={'source_id':r['id'],'observed_at_s':tm,'sequence':int(tm/5),'tls':r['tls'],'signal_state':c.trafficlight.getRedYellowGreenState(r['tls']),'scheduled_switch_s':c.trafficlight.getNextSwitch(r['tls']),'switch_is_prediction':True,'detectors':[{'id':s['id'],'vehicles':c.lanearea.getLastStepVehicleNumber(s['id']),'halting':c.lanearea.getLastStepHaltingNumber(s['id']),'occupancy_pct':c.lanearea.getLastStepOccupancy(s['id'])} for s in det]}
      positive+=any(x['vehicles']>0 for x in obs['detectors']);records+=1;f.write(json.dumps(obs)+'\n')
 finally:c.close()
 trips=list(ET.parse(o/'tripinfo.xml').getroot());stats=ET.parse(o/'statistics.xml').getroot();valid=len(ET.parse(o/'routes.rou.xml').getroot().findall('vehicle'))
 report={'city':city,'edges':len(n.getEdges()),'junctions':len(n.getNodes()),'signal_controllers':len(n.getTrafficLights()),'net_sha256':hashlib.sha256(netpath.read_bytes()).hexdigest(),'rsus':len(rsus),'e2_detectors':len(sensors),'observation_records':records,'observations_with_vehicles':positive,'valid_routes':valid,'arrived':sum(float(t.get('arrival',-1))>=0 for t in trips),'unfinished':sum(float(t.get('arrival',-1))<0 for t in trips),'max_running':peak,'statistics':{s.tag:s.attrib for s in stats},'status':'development; synthetic demand, inferred signal timing; no radio delivery or governance comparison yet'}
 (o/'validation.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':
 results=[]
 for city,bbox in CITIES.items():
  result=build(city,bbox);results.append(result);print(json.dumps(result),flush=True)
 (ROOT/'reports/three_city_infrastructure.json').write_text(json.dumps(results,indent=2))
