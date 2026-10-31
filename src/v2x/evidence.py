"""Observation-only receiver; source truth is never consulted."""
import math

class EvidenceReceiver:
    def __init__(self,max_age_s):
        if not math.isfinite(max_age_s) or max_age_s<0:raise ValueError('Invalid age limit')
        self.max_age_s=max_age_s;self.current=None;self.last_time=-math.inf
    def _advance(self,now):
        if not math.isfinite(now) or now<self.last_time:raise ValueError('Receiver clock must advance')
        self.last_time=now
    def receive(self,evidence,now):
        self._advance(now);stamp=evidence['observed_at_s']
        if not math.isfinite(stamp) or stamp>now:raise ValueError('Future or invalid observation')
        if self.current is not None and evidence['source_id']!=self.current['source_id']:raise ValueError('Different source')
        if now-stamp>self.max_age_s:return 'age_rejected'
        if self.current is not None:
            if evidence['sequence']<self.current['sequence']:return 'superseded_rejected'
            if evidence['sequence']==self.current['sequence']:return 'duplicate'
        self.current=dict(evidence);return 'updated'
    def available(self,now):
        self._advance(now)
        if self.current is None or now-self.current['observed_at_s']>self.max_age_s:return None
        return dict(self.current)

def freshness_intervals(updates,start,end,max_age_s):
    """Exact integration over [start,end]; updates contain accepted receipts only."""
    if not all(math.isfinite(x) for x in [start,end,max_age_s]) or end<=start or max_age_s<0:raise ValueError('Invalid window')
    previous=-math.inf
    for u in updates:
        if not all(math.isfinite(u[k]) for k in ['rx_s','observed_at_s']) or u['rx_s']<previous or not 0<=u['rx_s']-u['observed_at_s']<=max_age_s:raise ValueError('Invalid accepted update')
        previous=u['rx_s']
    cuts=sorted({start,end}|{u['rx_s'] for u in updates if start<u['rx_s']<end}|{u['observed_at_s']+max_age_s for u in updates if start<u['observed_at_s']+max_age_s<end})
    segments=[];i=0;latest=None;age_area=0;known_time=0;max_age=None
    for a,b in zip(cuts,cuts[1:]):
        while i<len(updates) and updates[i]['rx_s']<=a:latest=updates[i];i+=1
        if latest is None:state='missing'
        else:
            stamp=latest['observed_at_s'];age_a=a-stamp;age_b=b-stamp
            state='fresh' if (a+b)/2-stamp<=max_age_s else 'stale'
            age_area+=(age_a+age_b)*(b-a)/2;known_time+=b-a;max_age=max(max_age or 0,age_b)
        if segments and segments[-1]['state']==state:segments[-1]['end']=b
        else:segments.append({'start':a,'end':b,'state':state})
    durations={s:sum(x['end']-x['start'] for x in segments if x['state']==s) for s in ['fresh','stale','missing']}
    longest=run=0
    for x in segments:
        run=0 if x['state']=='fresh' else run+x['end']-x['start'];longest=max(longest,run)
    return segments,dict(durations,window_s=end-start,fresh_fraction=durations['fresh']/(end-start),mean_age_when_known_s=age_area/known_time if known_time else None,max_age_when_known_s=max_age,longest_unavailable_s=longest)
