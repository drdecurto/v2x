"""Prospective CO2 accounting checks on existing city/control configurations."""
import fcntl,gzip,json,subprocess,xml.etree.ElementTree as E
from collections import defaultdict
from v2x.credentials import ROOT
O=ROOT/'runs/co2_accounting_v1'
def save(p,x):p.write_text(json.dumps(x,indent=2))
def main():
 O.mkdir(exist_ok=True)
 with (O/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (O/'summary.json').exists():raise SystemExit('Completed')
  plan=dict(stage='development_accounting_not_confirmatory',cities=['los_angeles','luxembourg','pedralbes'],modes=['actuated','static'],seed=4101,end_s=2400,step_s=.5,emission_class='HBEFA3/PC_G_EU6',fleet='Homogeneous gasoline Euro6 archetype; not a claim about any city fleet',boundary='Modelled tank-to-wheel CO2; excludes fuel production, EV electricity, infrastructure and inference',uncompleted='Include accumulated emissions of unfinished trips; pending and excluded requests remain explicit',verification='Integrate unscaled mg/s output times0.5s and reconcile per vehicle against tripinfo CO2_abs in mg',source_docs=['https://sumo.dlr.de/docs/Simulation/Output/EmissionOutput.html','https://sumo.dlr.de/docs/Models/Emissions/HBEFA3-based.html'])
  if not (O/'plan.json').exists():save(O/'plan.json',plan)
  save(O/'accounting_amendment.json',dict(reason='First LA run failed exact rate/trip reconciliation. Preserve original plan and raw run. Primary reporting uses tripinfo movement-device totals including unfinished trips; rate integrals retained as diagnostics, not asserted identical.',source='SUMO1.27.1 MSDevice_Emissions::notifyMove versus MSEmissionExport::writeEmissions'))
  rows=[]
  for city in plan['cities']:
   for mode in plan['modes']:
    p=O/f'{city}_{mode}';p.mkdir(exist_ok=True)
    src=ROOT/'runs'/('city_preflight_v1' if mode=='actuated' else 'static_sensors_v1')/city
    tree=E.parse(ROOT/'runs/city_preflight_v1'/city/'accepted.xml')
    for v in tree.getroot().findall('vType'):v.set('emissionClass',plan['emission_class'])
    tree.write(p/'routes.xml',encoding='utf-8',xml_declaration=True)
    if not (p/'statistics.xml').exists():
     args=[str(ROOT/'.venv/bin/sumo'),'-n',str(src/'city.net.xml'),'-r',str(p/'routes.xml'),'--seed','4101','--end','2400','--step-length','.5','--time-to-teleport','-1','--no-step-log','--device.emissions.probability','1','--emission-output',str(p/'emissions.xml.gz'),'--emission-output.attributes','id,eclass,CO2','--emission-output.precision','8','--precision','8','--tripinfo-output',str(p/'tripinfo.xml'),'--tripinfo-output.write-unfinished','true','--statistic-output',str(p/'statistics.xml'),'--error-log',str(p/'errors.log')]
     save(p/'command.json',args)
     with (p/'run.log').open('w') as f:subprocess.run(args,stdout=f,stderr=f,check=True)
    totals=defaultdict(float);records=defaultdict(int)
    with gzip.open(p/'emissions.xml.gz','rb') as f:
     for event,element in E.iterparse(f,events=['end']):
      if element.tag=='vehicle':
       assert element.get('eclass')==plan['emission_class'];rate=float(element.get('CO2'));assert rate>=0
       ident=element.get('id');totals[ident]+=rate*.5;records[ident]+=1;element.clear()
      elif element.tag=='timestep':element.clear()
    trips=list(E.parse(p/'tripinfo.xml').getroot());assert set(totals)=={t.get('id') for t in trips}
    triptotals={t.get('id'):float(t.find('emissions').get('CO2_abs')) for t in trips}
    errors={i:abs(totals[i]-triptotals[i]) for i in totals}
    # Preserve failed exact reconciliation; outputs use different event hooks.
    exact_reconciliation=max(errors.values())<.001
    unfinished={t.get('id') for t in trips if float(t.get('arrival'))<0}
    prior={t.get('id'):t.attrib for t in E.parse(src/'tripinfo.xml').getroot()}
    unchanged=all(all(abs(float(t.get(k))-float(prior[t.get('id')][k])) <= (.00501 if k=='routeLength' else .000001) for k in ['arrival','duration','routeLength','waitingTime']) for t in trips)
    st=E.parse(p/'statistics.xml').getroot()
    row=dict(city=city,mode=mode,requested=600,accepted=len(trips),arrived=len(trips)-len(unfinished),unfinished=len(unfinished),pending=int(st.find('vehicles').get('waiting')),excluded=600-len(trips),co2_kg=sum(triptotals.values())/1e6,unfinished_co2_kg=sum(triptotals[i] for i in unfinished)/1e6,rate_integral_kg=sum(totals.values())/1e6,exact_reconciliation=exact_reconciliation,max_reconciliation_error_mg=max(errors.values()),trajectory_summary_matches_prior=unchanged,safety=st.find('safety').attrib)
    save(p/'per_vehicle.json',{i:dict(integrated_mg=totals[i],tripinfo_mg=triptotals[i],records=records[i],unfinished=i in unfinished) for i in totals});save(p/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
  save(O/'summary.json',rows)
if __name__=='__main__':main()
