"""Verify lane incompatibility from independent network and saved TraCI evidence."""
import json
import sumolib
from v2x.credentials import ROOT
p=ROOT/'runs/pedralbes_lane_diagnostic_v1';snapshots=json.loads((p/'snapshots.json').read_text());last=snapshots[-1];n=sumolib.net.readNet(str(ROOT/'data/derived/pedralbes/city.net.xml'),withInternal=True);result=[]
for ident in ['4','107','126']:
 v=next(x for x in last['vehicles'] if x['id']==ident);lane=n.getLane(v['lane']);target=v['route'][v['route_index']+1];outgoing=[c.getToLane().getEdge().getID() for c in lane.getOutgoing()]
 assert target not in outgoing and v['speed']==0 and v['stops']=='()'
 current=next(x for x in v['best_lanes'] if x[0]==v['lane']);assert not current[4]
 result.append({'vehicle':ident,'lane':v['lane'],'lane_length_m':lane.getLength(),'required_next_edge':target,'actual_outgoing_edges':outgoing,'route_continuation_available_from_current_lane':False,'waiting_s':v['waiting_s']})
assert result[1]['required_next_edge'] in result[2]['actual_outgoing_edges']
assert result[2]['required_next_edge'] in result[1]['actual_outgoing_edges']
report={'passed':True,'interpretation':'Three stopped queue heads cannot follow their routes from their current lanes. Vehicles 107/126 need opposite lanes of a 7.81 m segment. Root cause of lane selection and correct physical repair not yet established.','queue_heads':result}
(p/'queue_head_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
