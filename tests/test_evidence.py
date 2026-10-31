import pytest
from v2x.evidence import EvidenceReceiver,freshness_intervals

def test_evidence_expires_without_a_new_packet():
 r=EvidenceReceiver(5);r.receive(dict(source_id='s',sequence=1,observed_at_s=0),.1)
 assert r.available(5) is not None and r.available(5.001) is None
 assert r.current['sequence']==1

def test_future_hidden_updates_do_not_advance_consumer():
 r=EvidenceReceiver(5);r.receive(dict(source_id='s',sequence=1,observed_at_s=0),0)
 assert r.available(2)['sequence']==1
 assert r.receive(dict(source_id='s',sequence=3,observed_at_s=2),2)=='updated'
 assert r.receive(dict(source_id='s',sequence=2,observed_at_s=1),3)=='superseded_rejected'
 assert r.available(3)['sequence']==3

def test_exact_integral_includes_initial_missing_and_stale_gap():
 _,s=freshness_intervals([dict(rx_s=1,observed_at_s=0),dict(rx_s=8,observed_at_s=7)],0,10,5)
 assert s['missing']==1 and s['fresh']==6 and s['stale']==3
 assert s['longest_unavailable_s']==3
 assert s['mean_age_when_known_s']==pytest.approx(35.5/9)

def test_window_clips_updates_and_expiry():
 _,s=freshness_intervals([dict(rx_s=1,observed_at_s=0),dict(rx_s=20,observed_at_s=19)],2,9,5)
 assert s['fresh']==3 and s['stale']==4 and s['missing']==0

@pytest.mark.parametrize('now',[-1,float('nan')])
def test_invalid_receiver_time(now):
 r=EvidenceReceiver(5)
 with pytest.raises(ValueError):r.receive(dict(source_id='s',sequence=1,observed_at_s=0),now)
