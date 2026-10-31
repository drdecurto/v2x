import json,httpx
from v2x.credentials import ROOT
model='qwen2.5:14b'
last=''
with httpx.Client(base_url='http://127.0.0.1:11434',timeout=httpx.Timeout(60,read=180),trust_env=False) as client:
    with client.stream('POST','/api/pull',json={'model':model,'stream':True}) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            data=json.loads(line)
            if data.get('error'):raise RuntimeError(data['error'])
            status=data.get('status','')
            pct=int(100*data.get('completed',0)/data['total']) if data.get('total') else None
            marker=f'{status} {pct//10*10 if pct is not None else ""}'
            if marker!=last:print(marker,flush=True);last=marker
(ROOT/'reports/ollama_qwen_download.json').write_text(json.dumps({'model':model,'status':'completed'},indent=2))
