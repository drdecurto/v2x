"""Shared consumer gates for received observations; no simulator-truth input."""
from v2x.policy import common_valid,rules_valid

def consume(policy,advisory,receiver,now,*,before_junction,audited=None,verdict=None,deadline_fallback=False):
    if policy not in ('none','rules','content','deadline'):raise ValueError('Unknown policy')
    def reject(mode):return {'admit':False,'mode':mode,'text':False,'action':None}
    if not common_valid(advisory,now):return reject('invalid_or_expired')
    if not before_junction:return reject('decision_point_passed')
    current=receiver.available(now)
    if current is None:return reject('evidence_unavailable')
    # Common executable-action check uses received evidence, not true road state.
    if (advisory['action']=='main' and current['road_A_closed']) or (advisory['action']=='detour' and not current['road_B_available']):return reject('observed_route_unavailable')
    if policy=='none':return {'admit':True,'mode':'unchecked','text':True,'action':advisory['action']}
    if not rules_valid(advisory,current,now):return reject('rules_reject')
    if policy=='rules' or (policy=='deadline' and deadline_fallback):return {'admit':True,'mode':'verified_template','text':False,'action':advisory['action']}
    if audited is None:return reject('audit_missing')
    if audited['source_id']!=current['source_id'] or audited['sequence']!=current['sequence']:return reject('audit_version_changed')
    if not 0<=now-audited['observed_at_s']<=receiver.max_age_s:return reject('audit_evidence_age')
    if verdict!='accept':return reject('content_'+str(verdict))
    return {'admit':True,'mode':'content_accept','text':True,'action':advisory['action']}
