"""Bounded development validation; no LLM calls and no changes to pilot_v1."""
import fcntl,json,hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
import traci
from v2x.credentials import ROOT
from v2x.incident import LaneClosure,route_feasible,passenger_allowed

OUT=ROOT/'runs/incident_validation_v4'
DIRECT=['approach','main','exit'];DETOUR=['approach','detour1','detour2','exit']

def episode(case,seed):
    out=OUT/f'{case}-{seed}';out.mkdir(exist_ok=True)
    result=out/'result.json'
    if result.exists(): return json.loads(result.read_text())
    (out/'routes.xml').write_text('<routes><vType id="car" vClass="passenger" accel="2.6" decel="4.5" sigma="0.5"/><route id="direct" edges="approach main exit"/><vehicle id="focal" type="car" route="direct" depart="0" departSpeed="max"/></routes>')
    traci.start([str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(out/'routes.xml'),'--seed',str(seed),'--step-length','0.2','--no-step-log','true','--duration-log.disable','true','--time-to-teleport','-1','--tripinfo-output',str(out/'trips.xml'),'--tripinfo-output.write-unfinished','true','--error-log',str(out/'errors.log')],label='validate',numRetries=3)
    c=traci.getConnection('validate'); main=LaneClosure('main_0');alt=LaneClosure('detour1_0')
    events=[];samples=[];changed=False;restored=False;first_main=None;wait=0
    try:
        assert route_feasible(c,DIRECT) and route_feasible(c,DETOUR)
        assert not route_feasible(c,['approach','exit'])
        while c.simulation.getTime()<220 and c.simulation.getMinExpectedNumber():
            now=c.simulation.getTime()
            if now>=5 and not changed:
                changed=True
                if case!='open':main.close(c)
                if case=='both_blocked':alt.close(c)
                events.append({'time_s':now,'event':'incident','direct_feasible':route_feasible(c,DIRECT),'detour_feasible':route_feasible(c,DETOUR)})
                assert route_feasible(c,DIRECT)==(case=='open')
                assert route_feasible(c,DETOUR)==(case!='both_blocked')
                if case=='detour':c.vehicle.setRoute('focal',DETOUR)
            if now>=80 and changed and not restored:
                restored=True
                for cl in (main,alt):
                    if cl.active:cl.reopen(c)
                assert route_feasible(c,DIRECT) and route_feasible(c,DETOUR), {lane: {'allowed':c.lane.getAllowed(lane), 'disallowed':c.lane.getDisallowed(lane), 'links':c.lane.getLinks(lane)} for lane in ['approach_0','main_0','detour1_0','detour2_0']}
                events.append({'time_s':now,'event':'reopen'})
            c.simulationStep();now=c.simulation.getTime()
            if 'focal' in c.vehicle.getIDList():
                road=c.vehicle.getRoadID('focal');speed=c.vehicle.getSpeed('focal')
                if road=='main' and first_main is None:first_main=now
                if main.active:assert road!='main',('entered_closed_main',now)
                if alt.active:assert road!='detour1',('entered_closed_detour',now)
                if road=='approach' and speed<0.1:wait+=.2
                samples.append({'time_s':now,'road':road,'speed_m_s':speed,'main_passenger_allowed':passenger_allowed(c,'main_0')})
    finally:c.close()
    trip=next(x for x in ET.parse(out/'trips.xml').getroot() if x.get('id')=='focal')
    arrived=float(trip.get('arrival'))>=0
    assert arrived
    if case in ('wait','both_blocked'):assert first_main>=80 and wait>20
    if case=='detour':assert first_main is None and any(x['road']=='detour1' for x in samples)
    if case=='open':assert first_main<80
    r={'case':case,'seed':seed,'arrived':arrived,'travel_duration_s':float(trip.get('duration')),'waiting_on_approach_s':round(wait,3),'first_main_entry_s':first_main,'closed_lane_entries':0,'events':events}
    (out/'samples.json').write_text(json.dumps(samples));result.write_text(json.dumps(r,indent=2));return r

def main():
    OUT.mkdir(exist_ok=True)
    with (OUT/'execution.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        rows=[episode(case,seed) for case in ('open','wait','detour','both_blocked') for seed in (2101,2102,2103)]
        report={'stage':'development_validation_not_confirmatory','episodes':len(rows),'all_arrived':all(x['arrived'] for x in rows),'closed_lane_entries':sum(x['closed_lane_entries'] for x in rows),'network_sha256':hashlib.sha256((ROOT/'data/derived/network/network.net.xml').read_bytes()).hexdigest(),'means':{case:{key:sum(x[key] for x in rows if x['case']==case)/3 for key in ('travel_duration_s','waiting_on_approach_s')} for case in ('open','wait','detour','both_blocked')},'scope':'Single passenger vehicle, one-lane toy network; permissions closure begins at 5 s and reopens at 80 s. No collision, emergency-braking, congestion or field safety claim.'}
        (ROOT/'reports/incident_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
