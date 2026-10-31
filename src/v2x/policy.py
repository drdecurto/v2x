"""Policies receive observations; evaluator-only labels are never inputs."""

def common_valid(advisory, now):
    return (advisory['issued_s'] <= now < advisory['expires_s']
            and advisory['road'] == 'A' and advisory['action'] in ('main','detour'))

def rules_valid(advisory, evidence, now):
    if not common_valid(advisory,now):
        return False
    if advisory['claimed_closed'] != evidence['road_A_closed']:
        return False
    if advisory['action'] == 'detour':
        return evidence['road_A_closed'] and evidence['road_B_available']
    return not evidence['road_A_closed']

def decide(policy, advisory, evidence, now, budget_s, predicted_service_s, verdict=None):
    if not common_valid(advisory,now):
        return {'admit':False,'mode':'invalid_or_expired','delay_s':0.0,'text':False}
    if policy=='none':
        return {'admit':True,'mode':'unchecked','delay_s':0.0,'text':True}
    valid=rules_valid(advisory,evidence,now)
    if not valid:
        return {'admit':False,'mode':'rules_reject','delay_s':0.0,'text':False}
    if policy=='rules':
        return {'admit':True,'mode':'verified_template','delay_s':0.0,'text':False}
    if policy=='deadline' and predicted_service_s >= budget_s:
        return {'admit':True,'mode':'deadline_template','delay_s':0.0,'text':False}
    if verdict not in ('accept','reject','unsure'):
        return {'admit':False,'mode':'audit_error','delay_s':0.0,'text':False}
    return {'admit':verdict=='accept','mode':'content_'+verdict,'delay_s':predicted_service_s,'text':verdict=='accept'}
