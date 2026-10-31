import json,fcntl
import traci
from v2x.credentials import ROOT
p=ROOT/'runs/no_ramp_lane_inspection_v1';p.mkdir(exist_ok=True)
with (p/'lock').open('w') as f:
 fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (p/'snapshot.json').exists():raise SystemExit('completed')
 src=ROOT/'runs/pedralbes_import_sensitivity_v1/no_guessed_ramps'
 traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(src/'city.net.xml'),'-r',str(src/'routes.rou.xml'),'--seed','4101','--step-length','.5','--end','2400','--time-to-teleport','-1','--no-step-log','--error-log',str(p/'errors.log')],label='inspect',stdout=(p/'console.log').open('w'))
 c=traci.getConnection('inspect')
 try:
  while c.simulation.getTime()<2400:c.simulationStep()
  rows=[{'id':v,'lane':c.vehicle.getLaneID(v),'position':c.vehicle.getLanePosition(v),'speed':c.vehicle.getSpeed(v),'waiting':c.vehicle.getWaitingTime(v),'route':c.vehicle.getRoute(v),'route_index':c.vehicle.getRouteIndex(v),'best_lanes':c.vehicle.getBestLanes(v)} for v in c.vehicle.getIDList()]
  (p/'snapshot.json').write_text(json.dumps(rows,indent=2));print([(x['id'],x['lane']) for x in rows])
 finally:c.close()
