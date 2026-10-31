"""Finite chronological packet replay. No resampling, trace looping or IID loss."""
from bisect import bisect_right
import math

def replay_observations(packets, observations, *, epoch_s, max_age_s):
    if max_age_s < 0 or not math.isfinite(max_age_s):
        raise ValueError('Invalid age limit')
    times=[o['observed_at_s'] for o in observations]
    versions=[o['sequence'] for o in observations]
    if not times or any(b<=a for a,b in zip(times,times[1:])) or any(b<=a for a,b in zip(versions,versions[1:])):
        raise ValueError('Observations must have increasing times and versions')
    if len({o['source_id'] for o in observations})!=1:
        raise ValueError('A replay represents one source/link')
    emissions=[];arrivals=[];previous=-math.inf
    for i,p in enumerate(packets):
        offset=float(p['tx_offset_s'])
        if not math.isfinite(offset) or offset<0 or offset<=previous:raise ValueError('TX offsets must increase')
        previous=offset;tx=epoch_s+offset;j=bisect_right(times,tx)-1
        if j<0:raise ValueError('No causally available observation')
        if not isinstance(p['received'],bool):raise ValueError('received must be Boolean')
        record={'packet_index':i,'source_seq':int(p['seq']),'tx_s':tx,'observation_sequence':versions[j],'observed_at_s':times[j],'received':p['received']}
        if p['received']:
            delay=float(p['delay_s'])
            if not math.isfinite(delay) or delay<0:raise ValueError('Invalid receive delay')
            record['rx_s']=tx+delay;arrivals.append(record)
        emissions.append(record)
    current_version=-1;current=None;deliveries=[]
    for record in sorted(arrivals,key=lambda r:(r['rx_s'],r['packet_index'])):
        version=record['observation_sequence'];age=record['rx_s']-record['observed_at_s']
        if age>max_age_s:decision='age_rejected'
        elif version<current_version:decision='superseded_rejected'
        elif version==current_version:decision='duplicate'
        else:decision='updated';current_version=version;current=record
        deliveries.append(dict(record,decision=decision,age_s=age))
    return emissions,deliveries
