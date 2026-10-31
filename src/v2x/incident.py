"""Authoritative road permissions and observation-only consumer freshness checks.

Does not change the preserved speed-restriction pilot. Intended for subsequent stages.
"""
from dataclasses import dataclass

@dataclass
class LaneClosure:
    lane: str
    original_disallowed: tuple | None = None
    active: bool = False

    def close(self, conn):
        if self.active:
            raise ValueError('Closure already active')
        self.original_disallowed = tuple(conn.lane.getDisallowed(self.lane))
        conn.lane.setDisallowed(self.lane, sorted(set(self.original_disallowed) | {'passenger'}))
        self.active = True

    def reopen(self, conn):
        if not self.active:
            raise ValueError('Closure not active')
        conn.lane.setDisallowed(self.lane, list(self.original_disallowed))
        self.active = False


def passenger_allowed(conn, lane):
    return 'passenger' not in conn.lane.getDisallowed(lane)


def route_feasible(conn, edges):
    """Check current passenger permissions and lane connectivity for this 1-lane net."""
    if not edges:
        return False
    lanes = [f'{edge}_0' for edge in edges]
    if not all(passenger_allowed(conn, lane) for lane in lanes):
        return False
    return all(any(link[0] == b for link in conn.lane.getLinks(a))
               for a, b in zip(lanes, lanes[1:]))


def freshness_reason(advisory, audited_evidence, consumer_evidence, now,
                     max_evidence_age_s, before_junction):
    """Uses only received evidence, never hidden current simulator state.

A later version invalidates an old audit even if the Boolean road state has
    returned to its previous value. Delayed updates remain a measurable limitation.
    """
    if not advisory['issued_s'] <= now < advisory['expires_s']:
        return 'expired_or_future'
    if not before_junction:
        return 'decision_point_passed'
    for evidence in (audited_evidence, consumer_evidence):
        if not 0 <= now - evidence['observed_s'] <= max_evidence_age_s:
            return 'evidence_age'
    if audited_evidence['version'] != consumer_evidence['version']:
        return 'evidence_version_changed'
    return None
