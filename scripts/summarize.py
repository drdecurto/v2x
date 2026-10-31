import json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from v2x.credentials import ROOT
out=ROOT/'reports/figures';out.mkdir(exist_ok=True)
rows=json.loads((ROOT/'reports/pilot_results.json').read_text());df=pd.DataFrame(rows)
summary=df.groupby(['case','condition','policy']).agg(n=('seed','size'),mean_travel_s=('travel_duration_s','mean'),deadline_misses=('deadline_missed','sum'),acted=('acted','sum'),arrived=('arrived','sum')).reset_index()
summary.to_csv(ROOT/'reports/pilot_summary.csv',index=False)
measurement=[];raw={}
for name,path in [('Nebius Qwen3 30B','runs/nebius_development.jsonl'),('Ollama Llama3.1 8B','runs/ollama_development.jsonl'),('Ollama Qwen2.5 14B','runs/ollama_qwen2.5_14b_development.jsonl')]:
 p=ROOT/path
 if not p.exists():continue
 d=pd.read_json(p,lines=True);raw[name]=d
 measurement.append({'service':name,'n':len(d),'successful':int((d.status=='ok').sum()),'median_s':float(d.elapsed_s.median()),'min_s':float(d.elapsed_s.min()),'max_s':float(d.elapsed_s.max()),'first_s':float(d.elapsed_s.iloc[0]),'median_excluding_first_s':float(d.elapsed_s.iloc[1:].median()),'source':path})
(ROOT/'reports/inference_summary.json').write_text(json.dumps(measurement,indent=2))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.2,3.5))
for name,d in raw.items():ax.plot(range(1,len(d)+1),d.elapsed_s,'o-',ms=3,lw=1,label=name)
ax.set(xlabel='Request order (three repetitions of eight development fixtures)',ylabel='Client elapsed time (s)')
ax.legend(frameon=False,fontsize=8);fig.tight_layout();fig.savefig(out/'inference_latency.pdf');fig.savefig(out/'inference_latency.png',dpi=170);plt.close(fig)
tr=json.loads((ROOT/'reports/trace_manifest.json').read_text())['traces']
fig,ax=plt.subplots(figsize=(7.2,3.6))
for priority in (0,7):
 s=sorted([x for x in tr if x['configuration']['priority']==priority],key=lambda x:x['configuration']['packet_size'])
 ax.plot([x['configuration']['packet_size'] for x in s],[x['pdr'] for x in s],'o-',label=f'Source priority {priority}')
ax.set(xlabel='Source packet size (bytes)',ylabel='Delivery ratio within matched support',ylim=(0,1.05));ax.legend(frameon=False);fig.tight_layout();fig.savefig(out/'trace_delivery.pdf');fig.savefig(out/'trace_delivery.png',dpi=170);plt.close(fig)
# Deterministic verification, not a significance test.
assert len(df)==144 and df.arrived.all()
assert not df.loc[df.policy=='rules','harmful_text_exposed'].any()
assert len(df[['case','condition','seed','policy']].drop_duplicates())==len(df)
check={'episodes':len(df),'all_focal_trips_completed':bool(df.arrived.all()),'unique_factorial_cells':True,'all_rules_outputs_template_only':not bool(df.loc[df.policy=='rules','text_exposed'].any()),'type':'development integrity checks, not confirmatory evidence'}
(ROOT/'reports/PILOT_VALIDATION.json').write_text(json.dumps(check,indent=2))
print(json.dumps(measurement,indent=2))
