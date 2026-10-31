import json,fcntl
from pathlib import Path
import sumolib,traci
from v2x.credentials import ROOT
O=ROOT/'runs/la_gui_v5';O.mkdir(exist_ok=True);n=sumolib.net.readNet(str(ROOT/'data/derived/los_angeles/downtown.net.xml'))
with (O/'capture.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 traci.start([str(ROOT/'.venv/bin/sumo-gui'),'-c',str(ROOT/'runs/la_development_v1/busy/scenario.sumocfg'),'--gui-settings-file',str(ROOT/'data/derived/los_angeles/publication.view.xml'),'--additional-files',str(ROOT/'data/derived/los_angeles/publication.poly.xml'),'--start','--quit-on-end','--end','610','--window-size','1600,1000','--tripinfo-output',str(O/'trips.xml'),'--summary-output',str(O/'summary.xml'),'--statistic-output',str(O/'statistics.xml'),'--error-log',str(O/'errors.log') ],label='LA',numRetries=5)
 c=traci.getConnection('LA');records=[];view='View #0'
 try:
  c.gui.setSchema(view,'publication')
  for step in range(1205):
   c.simulationStep();t=c.simulation.getTime()
   for ident in c.simulation.getDepartedIDList():c.vehicle.setColor(ident,(30,120,185,255))
   if t in (600.,601.):
    if t==600:
     x0,y0,x1,y1=n.getBoundary();c.gui.setBoundary(view,x0,y0,x1,y1);name='downtown_overview.png'
    else:
     c.gui.setSchema(view,'detail');x,y=c.simulation.convertGeo(-118.253,34.048,fromGeo=True);c.gui.setBoundary(view,x-420,y-260,x+420,y+260);name='downtown_detail.png'
    c.gui.screenshot(view,str(O/name),width=1600,height=1000)
    records.append({'file':name,'request_time_s':t,'running_vehicles':c.vehicle.getIDCount(),'source':'Actual SUMO GUI viewport; busy synthetic demand, seed 4101','attribution':'© OpenStreetMap contributors, ODbL'})
 finally:c.close()
 (O/'manifest.json').write_text(json.dumps(records,indent=2));print(records)
