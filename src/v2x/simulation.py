"""Development SUMO episode. Remote calls are profiled separately, not in virtual time."""
import json,random,math
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
import traci
from .credentials import ROOT
from .policy import decide,rules_valid

def run_episode(row,policy,seed,condition,verdict,measured_delay,output):
    output.mkdir(parents=True,exist_ok=True)
    rng=random.Random(seed)
    departures=sorted([rng.uniform(0,9) for _ in range(3)]+[10]+[rng.uniform(12,35) for _ in range(5)])
    vehicles=[]
    for i,t in enumerate(departures):
        ident='focal' if t==10 else f'b{i}'
        vehicles.append(f'<vehicle id="{ident}" type="car" route="direct" depart="{t:.3f}" departSpeed="max"/>')
    (output/'routes.rou.xml').write_text('<routes><vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="13.89"/><route id="direct" edges="approach main exit"/>'+''.join(vehicles)+'</routes>')
    cmd=[str(ROOT/'.venv/bin/sumo'),'-n',str(ROOT/'data/derived/network/network.net.xml'),'-r',str(output/'routes.rou.xml'),'--seed',str(seed),'--step-length','0.2','--no-step-log','true','--duration-log.disable','true','--time-to-teleport','-1','--tripinfo-output',str(output/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--error-log',str(output/'sumo_errors.log')]
    label='episode'
    traci.start(cmd,label=label,verbose=False,numRetries=3)
    conn=traci.getConnection(label)
    issued=False;handled=False;pending=None;record={'case':row['case'],'policy':policy,'seed':seed,'condition':condition,'reference':row['reference']['label'],'received':True,'admitted':False,'acted':False,'text_exposed':False,'deadline_missed':False,'stale_rejected':False,'reopened':False,'status':'ok'}
    closure=row['evidence']['road_A_closed']
    if closure:conn.lane.setMaxSpeed('main_0',0.1)
    try:
        while conn.simulation.getTime()<300 and conn.simulation.getMinExpectedNumber()>0:
            conn.simulationStep();now=conn.simulation.getTime()
            if closure and now>=80:
                conn.lane.setMaxSpeed('main_0',13.89);closure=False;record['reopened']=True
            ids=conn.vehicle.getIDList()
            if 'focal' not in ids:continue
            edge=conn.vehicle.getRoadID('focal')
            if not issued and edge=='approach' and conn.vehicle.getLanePosition('focal')>=240:
                issued=True
                advisory=dict(row['advisory'],issued_s=now,expires_s=now+60)
                evidence=dict(row['evidence'],observed_s=now,road_A_closed=closure)
                remaining=conn.lane.getLength('approach_0')-conn.vehicle.getLanePosition('focal')
                budget=remaining/max(conn.vehicle.getSpeed('focal'),1)-0.2
                service=measured_delay
                radio=0.0;received=True
                if condition=='synthetic_5s':service=5.0
                elif condition=='instant':service=0.0
                elif condition=='see_1470':
                    trace=pd.read_csv(ROOT/'data/derived/see_parkinglot_1.csv')
                    sample=trace.iloc[random.Random(seed).randrange(len(trace))]
                    received=bool(sample.received);radio=float(sample.delay_s) if received else 0.0
                    record.update(trace_packet_seq=int(sample.seq),trace_offset_s=float(sample.tx_offset_s))
                # A calibration estimate is fixed independently of this episode's service realization.
                # For this first diagnostic only, use the condition's fixed nominal service budget.
                prediction=5.0 if condition=='synthetic_5s' else (0.0 if condition=='instant' else 1.0)
                result=decide(policy,advisory,evidence,now,budget,prediction,verdict)
                actual_service=service if result['mode'].startswith('content_') else 0.0
                due=now+actual_service+radio
                record.update(issued_s=now,decision_budget_s=budget,service_s=actual_service,radio_s=radio,received=received,admitted=result['admit'],mode=result['mode'],due_s=due)
                pending=(due,advisory,evidence,result)
                if not received:handled=True;record['mode']='radio_loss'
            if pending and not handled and now>=pending[0]:
                handled=True;due,advisory,evidence,result=pending
                if edge!='approach':record['deadline_missed']=True;continue
                # Common timestamp and evidence-version freshness gate at the consumer.
                # This pilot assumes immediate authoritative updates; lag is a future factor.
                if now>=advisory['expires_s'] or closure!=evidence['road_A_closed']:
                    record['stale_rejected']=True;continue
                if result['admit']:
                    record['text_exposed']=result['text']
                    route=['approach','main','exit'] if advisory['action']=='main' else ['approach','detour1','detour2','exit']
                    conn.vehicle.setRoute('focal',route);record['acted']=True
        record['end_s']=conn.simulation.getTime()
    finally:conn.close()
    trips=ET.parse(output/'tripinfo.xml').getroot()
    trip=next((x for x in trips if x.get('id')=='focal'),None)
    if trip is None:raise RuntimeError('Missing focal trip')
    record.update(travel_duration_s=float(trip.get('duration')),arrived=float(trip.get('arrival'))>=0,route_length_m=float(trip.get('routeLength')),time_loss_s=float(trip.get('timeLoss')))
    record['harmful_text_exposed']=record['text_exposed'] and record['reference']=='violating'
    record['legitimate_missed']=record['reference']=='clean' and not record['acted']
    (output/'result.json').write_text(json.dumps(record,indent=2))
    return record
