"""Reconcile every requested ID against exclusions and SUMO outcomes."""
import json,xml.etree.ElementTree as E
from v2x.credentials import ROOT
O=ROOT/'runs/city_preflight_v1';checks=[]
for row in json.loads((O/'summary.json').read_text()):
 p=O/row['city'];r=json.loads((p/'preflight.json').read_text());requested=set(r['requested_ids']);unroutable=set(r['unroutable']);bad={x['vehicle'] for x in r['lane_failures']};accepted=set(r['accepted_ids'])
 assert not(unroutable&bad or unroutable&accepted or bad&accepted)
 assert requested==unroutable|bad|accepted and len(requested)==600
 saved={v.get('id') for v in E.parse(p/'accepted.xml').getroot().findall('vehicle')};assert saved==accepted
 trips=list(E.parse(p/'tripinfo.xml').getroot());arrived={v.get('id') for v in trips if float(v.get('arrival'))>=0}
 assert arrived==accepted and len(trips)==len(accepted)==row['arrived']
 st=E.parse(p/'statistics.xml').getroot();assert st.find('vehicles').get('running')=='0' and st.find('vehicles').get('waiting')=='0'
 assert all(float(v)==0 for v in st.find('safety').attrib.values()) and st.find('teleports').get('total')=='0'
 warnings=[line for line in (p/'errors.log').read_text().splitlines() if 'no controlling detector' in line]
 checks.append({'city':row['city'],'request_ids_reconciled':len(requested),'arrivals_verified':len(arrived),'signal_detector_warning_lines':len(warnings),'passed':True})
# Compare semantics, excluding XML comments and generated timestamps, to prior Pedralbes candidate.
a=E.tostring(E.parse(O/'pedralbes/city.net.xml').getroot());b=E.tostring(E.parse(ROOT/'runs/pedralbes_lane_access_v1/no_guessed_ramps_lane_access/city.net.xml').getroot())
result={'cities':checks,'pedralbes_same_network_semantics_as_prior':a==b,'note':'Repeated Pedralbes seed4101 is construction replication, not additional independent evidence.'}
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
