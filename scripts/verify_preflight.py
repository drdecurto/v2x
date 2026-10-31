import json,xml.etree.ElementTree as E
from pathlib import Path
from v2x.credentials import ROOT
O=ROOT/'runs/preflight_validation_v1';checks=[]
def routes(path):
 return {v.get('id'):(v.get('depart'),v.find('route').get('edges')) for v in E.parse(path).getroot().findall('vehicle')}
assert routes(O/'4101/routed.xml')==routes(ROOT/'runs/pedralbes_lane_access_v1/no_guessed_ramps_lane_access/routes.rou.xml')
for seed in [4101,4102,4103]:
 p=O/str(seed);requests={v.get('id') for v in E.parse(p/'trips.xml').getroot().findall('trip')};r=json.loads((p/'preflight.json').read_text());u=set(r['unroutable']);bad={x['vehicle'] for x in r['lane_infeasible']};accepted=set(r['accepted_ids'])
 assert len(requests)==600 and not(u&bad or u&accepted or bad&accepted) and u|bad|accepted==requests
 full=routes(p/'routed.xml');filtered=routes(p/'accepted.xml');assert filtered=={i:full[i] for i in accepted}
 for arm in ['unfiltered','preflight']:
  trips=list(E.parse(p/arm/'tripinfo.xml').getroot());arrived={t.get('id') for t in trips if float(t.get('arrival',-1))>=0};unfinished={t.get('id') for t in trips if float(t.get('arrival',-1))<0}
  if arm=='preflight':assert arrived==accepted and not unfinished
  else:assert unfinished==bad and arrived==accepted
 checks.append({'seed':seed,'requested':600,'accepted_and_arrived':len(accepted),'unroutable':len(u),'lane_rejected':len(bad),'exact_unfiltered_stranded_match':True})
(O/'checks.json').write_text(json.dumps(checks,indent=2));print(checks)
