"""Independent decimal trip-total accounting; not validation of physical emissions."""
from decimal import Decimal
import json,xml.etree.ElementTree as E
from v2x.credentials import ROOT
O=ROOT/'runs/co2_accounting_v1';checks=[]
for row in json.loads((O/'summary.json').read_text()):
 p=O/(row['city']+'_'+row['mode']);vehicles=E.parse(p/'routes.xml').getroot().findall('vehicle');ids={v.get('id') for v in vehicles};trips=list(E.parse(p/'tripinfo.xml').getroot());seen=set();total=Decimal(0);unfinished=Decimal(0)
 for t in trips:
  ident=t.get('id');assert ident in ids and ident not in seen;seen.add(ident)
  value=Decimal(t.find('emissions').get('CO2_abs'));assert value.is_finite() and value>=0;total+=value
  if Decimal(t.get('arrival'))<0:unfinished+=value
 assert seen==ids
 assert abs(total/Decimal(1000000)-Decimal(str(row['co2_kg'])))<Decimal('0.000000001')
 assert abs(unfinished/Decimal(1000000)-Decimal(str(row['unfinished_co2_kg'])))<Decimal('0.000000001')
 assert row['arrived']+row['unfinished']+row['pending']+row['excluded']==600
 assert row['trajectory_summary_matches_prior']
 checks.append(dict(city=row['city'],mode=row['mode'],vehicle_ids_checked=len(seen),trip_total_verified=True,rate_integral_minus_trip_percent=100*(row['rate_integral_kg']/row['co2_kg']-1),exact_rate_trip_reconciliation=row['exact_reconciliation']))
(O/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
