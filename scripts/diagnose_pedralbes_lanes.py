"""Read-only traffic observation: no repair, rerouting or signal override."""
import json,fcntl,xml.etree.ElementTree as E
from collections import Counter
import traci
from v2x.credentials import ROOT
p=ROOT/'runs/pedralbes_lane_diagnostic_v1';p.mkdir(exist_ok=True)
with (p/'run.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (p/'summary.json').exists():raise SystemExit('Already completed')
 src=ROOT/'runs/city_infrastructure_v2/pedralbes'
 t=E.parse(src/'infrastructure.add.xml')
 for e in t.getroot():
  if e.tag=='laneAreaDetector':e.set('file',str(p/'detectors.xml'))
 t.write(p/'infrastructure.add.xml')
 traci.start([str(ROOT/'.venv/bin/sumo'),'-c',str(src/'scenario.sumocfg'),'--additional-files',str(p/'infrastructure.add.xml'),'--end','3600','--tripinfo-output',str(p/'tripinfo.xml'),'--statistic-output',str(p/'statistics.xml'),'--error-log',str(p/'errors.log')],label='diagnostic',stdout=(p/'console.log').open('w'))
 c=traci.getConnection('diagnostic');snapshots=[];mismatch=[]
 try:
  while c.simulation.getTime()<3600:
   c.simulationStep();tm=c.simulation.getTime()
   if tm%5==0 and tm<=900:
    for detector in [e.get('id') for e in t.getroot() if e.tag=='laneAreaDetector']:
     nv=c.lanearea.getLastStepVehicleNumber(detector);nh=c.lanearea.getLastStepHaltingNumber(detector)
     if nh>nv:
      lid=c.lanearea.getLaneID(detector)
      mismatch.append({'time':tm,'detector':detector,'vehicle_count':nv,'halting_count':nh,'reported_ids':c.lanearea.getLastStepVehicleIDs(detector),'lane':lid,'lane_vehicles':[{'id':v,'position':c.vehicle.getLanePosition(v),'speed':c.vehicle.getSpeed(v),'length':c.vehicle.getLength(v)} for v in c.lane.getLastStepVehicleIDs(lid)],'start':c.lanearea.getPosition(detector),'length':c.lanearea.getLength(detector)})
   if tm in [900,1800,2400,3000,3600]:
    vehicles=[]
    for v in c.vehicle.getIDList():
     vehicles.append({'id':v,'lane':c.vehicle.getLaneID(v),'position':c.vehicle.getLanePosition(v),'speed':c.vehicle.getSpeed(v),'waiting_s':c.vehicle.getWaitingTime(v),'leader':c.vehicle.getLeader(v,100),'next_tls':c.vehicle.getNextTLS(v),'route':c.vehicle.getRoute(v),'route_index':c.vehicle.getRouteIndex(v),'best_lanes':c.vehicle.getBestLanes(v),'lane_links':c.lane.getLinks(c.vehicle.getLaneID(v),extended=True),'stops':str(c.vehicle.getStops(v))})
    snapshots.append({'time':tm,'running':len(vehicles),'vehicles':vehicles,'signals':[{'id':s,'state':c.trafficlight.getRedYellowGreenState(s),'phase':c.trafficlight.getPhase(s),'next_switch':c.trafficlight.getNextSwitch(s)} for s in c.trafficlight.getIDList()]})
 finally:c.close()
 (p/'snapshots.json').write_text(json.dumps(snapshots,indent=2));(p/'detector_mismatches.json').write_text(json.dumps(mismatch,indent=2))
 summary={'snapshots':[{'time':s['time'],'running':s['running'],'waiting_over_600s':sum(v['waiting_s']>600 for v in s['vehicles']),'top_lanes':Counter(v['lane'] for v in s['vehicles']).most_common(8)} for s in snapshots],'mismatches':len(mismatch),'method':'same demand and control, horizon extended to 3600; no repair or rerouting'}
 (p/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
