"""Actual SUMO GUI viewport exports of the validated single-vehicle scenario."""
import json,fcntl
from pathlib import Path
import traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure
OUT=ROOT/'runs/gui_capture_v2';OUT.mkdir(exist_ok=True)
with (OUT/'capture.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 records=[]
 for case in ['wait','detour']:
  traci.start([str(ROOT/'.venv/bin/sumo-gui'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(ROOT/f'runs/incident_validation_v4/{case}-2101/routes.xml'),'--seed','2101','--step-length','0.2','--start','--quit-on-end','--no-step-log','true','--duration-log.disable','true','--window-size','1400,900','--error-log',str(OUT/f'{case}_errors.log')],label='screens',numRetries=45)
  c=traci.getConnection('screens');cl=LaneClosure('main_0');view='View #0';closed=False;opened=False
  try:
   c.gui.setSchema(view,'standard');c.gui.setBoundary(view,-40,-100,1240,560)
   while c.simulation.getTime()<90:
    now=c.simulation.getTime()
    if now>=5 and not closed:
     cl.close(c);closed=True
     if case=='detour':c.vehicle.setRoute('focal',['approach','detour1','detour2','exit'])
    if now>=80 and not opened:cl.reopen(c);opened=True
    if 'focal' in c.vehicle.getIDList():c.vehicle.setColor('focal',(220,40,40,255))
    if (case=='wait' and now in (35.,85.)) or (case=='detour' and now==35.):
     x,y=c.vehicle.getPosition('focal');c.gui.setBoundary(view,x-90,y-45,x+90,y+45)
     name=f'{case}_{int(now)}.png';c.gui.screenshot(view,str(OUT/name),width=1400,height=800)
     records.append({'file':name,'requested_sim_s':now,'case':case,'road':c.vehicle.getRoadID('focal'),'position':c.vehicle.getPosition('focal'),'main_closed':cl.active,'note':'SUMO GUI screenshot is produced on the next simulation step; viewport export, not an AI-generated scene.'})
    c.simulationStep()
  finally:c.close()
 (OUT/'manifest.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
