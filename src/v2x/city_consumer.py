"""Bind a received-evidence decision to immutable, preflighted city routes.

No simulator, future outcome or CO2-counterfactual input is accepted. The
caller must supply current received evidence and an explicit route-choice gate.
"""
from v2x.consumer import consume


def consume_city(policy, advisory, receiver, now, *, vehicle_id, original_route,
                 alternative_route, before_decision, compliant, audited=None,
                 verdict=None, deadline_fallback=False):
    result = consume(policy, advisory, receiver, now,
                     before_junction=before_decision, audited=audited,
                     verdict=verdict, deadline_fallback=deadline_fallback)
    result = dict(result, vehicle_id=vehicle_id, route_selected=False, route=None,
                  delivered_text=None)
    if not result['admit']:
        return result
    route = original_route if result['action'] == 'main' else alternative_route
    if not route:
        return dict(result, admit=False, mode='no_preflighted_route', text=False,
                    action=None)
    if result['text']:
        result['delivered_text'] = advisory['text']
    elif result['action'] == 'detour':
        result['delivered_text'] = ('The received road observation reports a closure. '
                                    'An alternative route is available. No emissions saving is guaranteed.')
    else:
        result['delivered_text'] = 'The received road observation reports the original route open.'
    # Admission is distinct from driver action; the same compliance draw is reused.
    result['route_selected'] = bool(compliant)
    result['route'] = list(route) if compliant else None
    return result
