"""Unaltered simulator viewport exports; hypothetical RSUs marked orange."""
import json,os
from pathlib import Path
import traci,sumolib
from v2x.credentials import ROOT
for city in ['los_angeles','luxembourg','pedralbes']:
 src=ROOT/'runs/city_infrastructure_v2'/city
 if not (src/'validation.json').exists():continue
 out=ROOT/'runs/city_gui_v1'/city;out.mkdir(parents=True,exist_ok=True)
 if (out/'manifest.json').exists():continue
 d=ROOT/'data/derived'/city;n=sumolib.net.readNet(str(d/('downtown.net.xml' if city=='los_angeles' else 'city.net.xml')))
 infrastructure=json.loads((src/'infrastructure.json').read_text());rsu=infrastructure['rsus'][0]
 # Redirect detector output too, so rendering never overwrites the complete smoke test.
 import xml.etree.ElementTree as ET
 tree=ET.parse(src/'infrastructure.add.xml')
 for element in tree.getroot():
  if element.tag=='laneAreaDetector':element.set('file',str(out/'detector_intervals.xml'))
 tree.write(out/'infrastructure.add.xml')
 args=[str(ROOT/'.venv/bin/sumo-gui'),'-c',str(src/'scenario.sumocfg'),'--additional-files',str(d/'publication.poly.xml')+','+str(out/'infrastructure.add.xml'),'--start','--quit-on-end','--end','605','--window-size','1600,1000','--tripinfo-output',str(out/'trips.xml'),'--statistic-output',str(out/'statistics.xml'),'--error-log',str(out/'errors.log')]
 traci.start(args,label=city,numRetries=5);c=traci.getConnection(city);records=[]
 try:
  c.gui.setSchema('View #0','publication')
  while c.simulation.getTime()<602:
   c.simulationStep();t=c.simulation.getTime()
   for v in c.simulation.getDepartedIDList():c.vehicle.setColor(v,(30,120,185,255))
   if t==600:
    x0,y0,x1,y1=n.getBoundary();c.gui.setBoundary('View #0',x0,y0,x1,y1);name='overview.png'
   elif t==601:
    x,y=rsu['x'],rsu['y'];c.gui.setBoundary('View #0',x-450,y-280,x+450,y+280);name='detail.png'
   else:continue
   c.gui.screenshot('View #0',str(out/name),width=1600,height=1000)
   records.append({'file':name,'requested_time_s':t,'actual_export_next_step_s':t+.5,'vehicles':c.vehicle.getIDCount(),'center_rsu':rsu if name=='detail.png' else None,'attribution':'© OpenStreetMap contributors','vehicle_visual_scale':2.5,'note':'Actual SUMO viewport; synthetic traffic and hypothetical roadside infrastructure'})
 finally:c.close()
 (out/'manifest.json').write_text(json.dumps(records,indent=2));print(city,records,flush=True)
