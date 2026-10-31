"""Choose a development closure candidate by route exposure, not audit outcomes."""
from collections import Counter
import json,heapq,xml.etree.ElementTree as E
from v2x.credentials import ROOT
import sumolib
net=sumolib.net.readNet(str(ROOT/'data/derived/los_angeles/downtown.net.xml'))
routes=[v.find('route').get('edges').split() for v in E.parse(ROOT/'runs/la_development_v1/busy/routes.rou.xml').getroot().findall('vehicle')]
counts=Counter(edge for r in routes for edge in r[1:-1])
candidates=[e for e in net.getEdges() if e.getName() in ['South Figueroa Street','South Broadway','South Hill Street'] and e.getLength()>60]
chosen=max(candidates,key=lambda e:counts[e.getID()]);blocked=chosen.getID()
def path(start,end):
 q=[(0,start,[start])];seen=set()
 while q:
  cost,edge,route=heapq.heappop(q)
  if edge in seen:continue
  seen.add(edge)
  if edge==end:return route,cost
  for nxt,conns in net.getEdge(edge).getOutgoing().items():
   if nxt.getID()==blocked:continue
   if any(c.getFromLane().allows('passenger') and c.getToLane().allows('passenger') for c in conns):heapq.heappush(q,(cost+nxt.getLength(),nxt.getID(),route+[nxt.getID()]))
 return None,None
examples=[]
for route in routes:
 if blocked not in route[1:-1]:continue
 alt,length=path(route[0],route[-1])
 if alt:
  examples.append({'original_route':route,'alternative_route':alt,'alternative_length_excluding_first_edge_m':length});break
assert examples and blocked not in examples[0]['alternative_route']
result={'status':'development closure candidate; no closure traffic experiment yet','selection':'Highest route count among >=60 m segments on three named downtown arterials, using synthetic busy demand only','edge':blocked,'street':chosen.getName(),'length_m':chosen.getLength(),'lane_count':len(chosen.getLanes()),'routes_through_interior':counts[blocked],'examples':examples}
(ROOT/'config/la_incident_candidate.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k!='examples'})
