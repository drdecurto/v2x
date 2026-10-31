"""Reconcile selected reruns and characterize, without inferring policy effects."""
import json,xml.etree.ElementTree as E
from decimal import Decimal
from pathlib import Path
from v2x.credentials import ROOT
O=ROOT/'runs/reopening_diagnostic_v2';summary=[]
for city,seed in [('los_angeles',4211),('luxembourg',4219),('pedralbes',4219)]:
 p=O/city/str(seed);prior=ROOT/'runs/replication_dynamics_v1'/city/str(seed)
 row=json.loads((p/'result.json').read_text());original=json.loads((prior/'result.json').read_text());assert row==original
 assert json.loads((p/'decisions.json').read_text())==json.loads((prior/'decisions.json').read_text())
 perms=json.loads((p/'permissions.json').read_text());assert len(perms)==1 and perms[0]['time_s']==900
 assert all(x['actual']==x['expected'] for x in perms[0]['lanes'].values())
 trips=E.parse(p/'tripinfo.xml').getroot().findall('tripinfo');assert row['arrived']==sum(float(t.get('arrival'))>=0 for t in trips)
 assert Decimal(row['co2_kg'])==sum((Decimal(t.find('emissions').get('CO2_abs')) for t in trips),Decimal(0))/1000000
 snapshots=json.loads((p/'snapshots.json').read_text());last=snapshots[-1]['vehicles'];assert len(last)==row['running']
 net=E.parse(ROOT/'runs/city_preflight_v1'/city/'city.net.xml').getroot();lane_edges={l.get('id'):edge.get('id') for edge in net.findall('edge') for l in edge.findall('lane')};connections={}
 for edge in net.findall('edge'):
  for l in edge.findall('lane'):connections[l.get('id')]=[]
 for c in net.findall('connection'):connections.setdefault(c.get('from')+'_'+c.get('fromLane'),[]).append(c.get('to'))
 blocked=[]
 for ident,v in last.items():
  if v['road'].startswith(':') or v['index']+1>=len(v['route']):continue
  nxt=v['route'][v['index']+1]
  outgoing={lane_edges[l[0]] for l in v['links']}
  if v['speed_m_s']<.1 and v['lane_length_m']-v['position_m']<1 and nxt not in outgoing:
   siblings=[lane for lane,edge in lane_edges.items() if edge==v['road'] and nxt in connections.get(lane,[])]
   blocked.append(dict(vehicle_id=ident,lane=v['lane'],next_route_edge=nxt,compatible_lanes_on_same_edge=siblings,waiting_s=v['waiting_s'],leader=v['leader']))
 summary.append(dict(city=city,seed=seed,prior_outcomes_reproduced=True,permissions_restored=True,running=row['running'],stopped=sum(v['speed_m_s']<.1 for v in last.values()),lane_end_without_next_route_connection=blocked,active_counts=[dict(time_s=x['time_s'],active=len(x['vehicles'])) for x in snapshots]))
(O/'analysis.json').write_text(json.dumps(dict(stage='outcome_selected_development_diagnostic',checks_passed=True,cases=summary),indent=2))
for r in summary:print(r['city'],r['running'],r['stopped'],len(r['lane_end_without_next_route_connection']))
