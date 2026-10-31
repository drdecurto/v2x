import json,shutil,xml.etree.ElementTree as E
from pathlib import Path
from v2x.credentials import ROOT
out=ROOT/'scenarios/three_city_v1';out.mkdir(parents=True,exist_ok=True)
for c in ['los_angeles','luxembourg','pedralbes']:
 p=out/c;p.mkdir(exist_ok=True);d=ROOT/'data/derived'/c;r=ROOT/'runs/city_infrastructure_v2'/c
 for src,dst in [(d/('downtown.net.xml' if c=='los_angeles' else 'city.net.xml'),'city.net.xml'),(d/'publication.poly.xml','buildings.poly.xml'),(d/'publication.view.xml','view.xml'),(r/'routes.rou.xml','routes.rou.xml'),(ROOT/'data/raw'/c/'source.json','source.json'),(r/'infrastructure.json','infrastructure.json'),(r/'validation.json','recorded_validation.json')]:shutil.copy2(src,p/dst)
 t=E.parse(r/'infrastructure.add.xml')
 for e in t.getroot():
  if e.tag=='laneAreaDetector':e.set('file','detector_intervals.xml')
 t.write(p/'infrastructure.add.xml',encoding='utf-8',xml_declaration=True)
 t=E.parse(r/'scenario.sumocfg');t.find('./input/net-file').set('value','city.net.xml');t.find('./input/additional-files').set('value','buildings.poly.xml,infrastructure.add.xml');t.find('./gui_only/gui-settings-file').set('value','view.xml');t.write(p/'scenario.sumocfg',encoding='utf-8',xml_declaration=True)
(out/'README.txt').write_text('THREE-CITY DEVELOPMENT SCENARIOS\nSUMO 1.27.1. Open any city/scenario.sumocfg in SUMO GUI, or run sumo-gui -c city/scenario.sumocfg.\nRoad geometry: © OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright.\nDerived networks distributed under ODbL. Source URLs, bounds and hashes in each source.json; no claim of actual municipal signal schedules or sensor installations. Synthetic passenger demand, seed 4101, departures 0-900s, simulation 0-2400s. No teleportation.\nOrange markers: hypothetical RSUs; cyan: E2 detectors. Inferred actuated signals use their own automatic detectors; E2 provides observations.\nExisting records are development diagnostics. Pedralbes has 66 running and 2 pending vehicles at cutoff; retain unfinished trips. Source observation logging requires the project build script; GUI configs output detector intervals only. No radio simulation or model calls occur when opening these scenarios.\n')
print(out)
