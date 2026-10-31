"""Necessary (not sufficient) route feasibility with legal lane changes.
Allows unlimited distance for permitted lane changes, so success is not a guarantee
of dynamic feasibility. Failure proves no legal lane sequence in this abstraction.
"""
import json,xml.etree.ElementTree as E
from collections import Counter
import sumolib
from v2x.credentials import ROOT

def audit(netpath,routepath):
 n=sumolib.net.readNet(str(netpath),withInternal=True);xml=E.parse(netpath).getroot();attrs={l.get('id'):l.attrib for e in xml.findall('edge') for l in e.findall('lane')}
 def closure(lanes):
  reached=set(lanes);todo=list(lanes)
  while todo:
   lid=todo.pop();lane=n.getLane(lid);siblings=lane.getEdge().getLanes();idx=lane.getIndex()
   for offset,key in [(1,'changeLeft'),(-1,'changeRight')]:
    j=idx+offset
    if j<0 or j>=len(siblings):continue
    allowed=attrs[lid].get(key)
    if allowed is not None and 'passenger' not in allowed.split() and 'all' not in allowed.split():continue
    target=siblings[j]
    if target.allows('passenger') and target.getID() not in reached:reached.add(target.getID());todo.append(target.getID())
  return reached
 bad=[];count=0
 for v in E.parse(routepath).getroot().findall('vehicle'):
  count+=1;edges=v.find('route').get('edges').split();reachable={l.getID() for l in n.getEdge(edges[0]).getLanes() if l.allows('passenger')}
  for before,after in zip(edges,edges[1:]):
   reachable=closure(reachable);next_lanes=set()
   for lid in reachable:
    for c in n.getLane(lid).getOutgoing():
     to=c.getToLane();via=c.getViaLaneID()
     if to.getEdge().getID()==after and to.allows('passenger') and (not via or n.getLane(via).allows('passenger')):next_lanes.add(to.getID())
   if not next_lanes:
    bad.append({'vehicle':v.get('id'),'from_edge':before,'to_edge':after,'reachable_lanes':sorted(reachable)});break
   reachable=next_lanes
 return {'routed':count,'necessary_check_failed':len(bad),'failures':bad,'note':'Pass does not establish enough distance for lane changes, traffic clearance or calibration.'}
if __name__=='__main__':
 cases={'original':(ROOT/'data/derived/pedralbes/city.net.xml',ROOT/'runs/city_infrastructure_v2/pedralbes/routes.rou.xml')}
 for label,folder in [('no_ramps','pedralbes_import_sensitivity_v1/no_guessed_ramps'),('lane_access','pedralbes_lane_access_v1/no_guessed_ramps_lane_access')]:
  d=ROOT/'runs'/folder;cases[label]=(d/'city.net.xml',d/'routes.rou.xml')
 report={k:audit(*paths) for k,paths in cases.items()};(ROOT/'reports/lane_route_audit.json').write_text(json.dumps(report,indent=2));print({k:(v['routed'],v['necessary_check_failed']) for k,v in report.items()})
