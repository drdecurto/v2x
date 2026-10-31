# Live received-evidence integration

Prospective plan: runs/live_stream_v1/plan.json, written before execution. One seed (6101), stationary LTE profile6, one advisory per episode, content consumer, fixed2s control and one local Qwen2.5:14b call. No warm-up, retries or remote API requests. The common adapter receives only transported observations, not simulator truth.

Online source observations every5s; closure5s/reopen18s; issue11s. Native chronological transmission selects the latest causally available observation. Native arrivals are processed at the next0.1s simulation step, maximum added delay99.988ms. The first40s are wall-clock paced; subsequent trip drain is accelerated. Per episode:1750TX,537lost,1212processed,one received packet still in transit at40s. No looping or resampling.

Fixed control:2.005384s service, consumed13.1s, detour applied;21 pending simulation steps. Local:14.995196s service including10.650746s server-reported load, consumed26s, accept verdict withheld because route-choice point passed;150 pending steps. Received version had also advanced, but the decision-point gate is the first rejection and must be reported as such. Max pacing lag19.170ms(control),12.679ms(local).

Trips arrive in120.9s(control detour) and81.6s(local late advice withheld). Preserve this unfavorable descriptive difference. Zero closed-lane entries during incident; SUMO error logs empty. One call is not a latency distribution, and two episodes do not identify a policy effect. The component map is not a city experiment. No5G/6G or urban radio validation.

Independent verifier reconciles native packet timestamps, loss, source causality, delayed processing, receiver updates, consumer decisions and live completion ordering.33 unit tests pass. Logs of incomplete episodes prevent silent repeated inference. Raw transport records remain local. Next: common city preflight and frozen workload/held-out protocol, then bounded multi-model comparisons.
