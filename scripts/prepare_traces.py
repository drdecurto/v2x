import json,hashlib
from pathlib import Path
import pandas as pd
from v2x.credentials import ROOT
from v2x.traces import align_packets
(ROOT/'data/derived').mkdir(parents=True,exist_ok=True)
base=ROOT/'data/raw/see_parkinglot/outdoor_parkinglot/1_tx'
configs=pd.read_csv(base/'parameters.csv');summary=[]
for _,cfg in configs.iterrows():
    folder=base/str(cfg['id'])
    packets,stats=align_packets(pd.read_csv(folder/'tx_t1.csv'),pd.read_csv(folder/'rx_t3_tx_t1.csv'))
    output=ROOT/f'data/derived/see_parkinglot_{cfg["id"]}.csv'
    packets[['tx_offset_s','received','delay_s','packet_size','seq']].to_csv(output,index=False)
    vals=packets.loc[packets.received,'delay_s']
    stats.update(configuration=cfg.to_dict(),duration_s=float(packets.tx_offset_s.max()),delay_median_ms=float(vals.median()*1000),delay_p95_ms=float(vals.quantile(.95)*1000),derived_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    summary.append(stats)
archive=ROOT/'data/raw/see_v2x_outdoor_parkinglot.tar.gz'
result={'dataset':'SEE-V2X outdoor parking lot, one transmitter','source':'https://cisl.ucr.edu/SEE-V2X/','doi':'10.1145/3715014.3722077','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'use':'Measured LTE C-V2X sidelink trace sensitivity, not NR/5G field validation; stationary parking-lot conditions do not establish urban mobility generalization.','license_status':'No explicit dataset license found in inspected README; keep raw data local and do not redistribute pending verification.','traces':summary}
(ROOT/'reports/trace_manifest.json').write_text(json.dumps(result,indent=2))
for s in summary:print(s['configuration']['id'],s['configuration']['packet_size'],'PDR',round(s['pdr'],4),'p95_ms',round(s['delay_p95_ms'],3),'excluded',s['boundary_tx_excluded'])
