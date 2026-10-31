import json
from datetime import datetime, timezone
import httpx
from v2x.credentials import ROOT, credentials
base, key = credentials()
try:
    with httpx.Client(timeout=30, follow_redirects=False, trust_env=False) as c:
        r = c.get(base + 'models', headers={'Authorization': 'Bearer ' + key})
        if r.status_code != 200:
            raise RuntimeError('Catalogue request returned HTTP ' + str(r.status_code))
        ids = sorted(x['id'] for x in r.json()['data'])
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'endpoint': base, 'models': ids}
    (ROOT/'reports/nebius_catalogue.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'endpoint': base, 'model_count': len(ids), 'models': ids}, indent=2))
except (httpx.HTTPError, ValueError, RuntimeError) as e:
    print('Catalogue check failed:', type(e).__name__)
    raise SystemExit(1)
